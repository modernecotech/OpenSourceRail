# Arusha — Urban Rail Network

**Country:** TZ · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Arusha-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.40 bn (88.5%) of external capital** and **$4.27 bn of external interest**. Capital plus saved interest totals **$7.67 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **18 lines**, including **15 additional residential lines**. **72.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **52.862 km to 83.484 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **79 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**18 line-local depots** provide **390 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **390 light-metro-3car trainsets / 1170 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Arusha rail network on OpenStreetMap](arusha-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 18 / 79 / 20 |
| Route length | 106.8 km double track |
| Direct transfers / reachable line pairs | 13.7% / 100.0% |
| Residents within 800 m radial station catchments | 463,298 (2020 raster; 57.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 390 × 3-car `light-metro-3car` trainsets (341 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,410,560 passenger-trips/day |
| Annual paid-trip planning range | 439.9–703.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.3 km | 8 | 45 | NW Mid ↔ SE Mid |
| line-2 | 17.1 km | 13 | 57 | SW Mid ↔ E Outer |
| line-3 | 22.9 km | 15 | 75 | S Outer ↔ NW Outer |
| line-4 |  2.7 km | 2 | 11 | W Inner ↔ W Inner |
| line-5 |  3.7 km | 3 | 14 | E Inner ↔ NE Inner |
| line-6 |  2.3 km | 2 | 10 | E Inner ↔ SE Mid |
| line-7 |  3.2 km | 3 | 14 | SW Mid ↔ S Mid |
| line-8 |  2.7 km | 2 | 11 | NW Mid ↔ NW Inner |
| line-9 |  3.1 km | 3 | 14 | E Mid ↔ SE Mid |
| line-10 |  2.3 km | 2 | 10 | NW Outer ↔ NW Outer |
| line-11 |  2.3 km | 3 | 13 | W Inner ↔ SW Inner |
| line-12 |  4.8 km | 4 | 18 | NE Inner ↔ N Inner |
| line-13 |  3.1 km | 2 | 12 | E Outer ↔ E Mid |
| line-14 |  3.3 km | 3 | 14 | E Outer ↔ NE Mid |
| line-15 |  4.0 km | 3 | 15 | S Mid ↔ SW Mid |
| line-16 |  2.0 km | 2 | 10 | E Mid ↔ NE Mid |
| line-17 |  7.9 km | 5 | 29 | NW Mid ↔ W Outer |
| line-18 |  4.8 km | 4 | 18 | S Inner ↔ W Mid |
| **Total** | **106.8 km** | **79 unique** | **390** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 8,370 one-way journeys / 49,660 train-km/day |
| Annual traction demand | 234.9 GWh |
| Station/depot PV / storage | 106.5 MW / 747.5 MWh |
| Aggregate charging power | 36.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-17: 4.6 km / 39 kWh |
| Lowest traversal charging margin | line-14: 19 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $965 M |
| Stations | $404 M |
| Depots | $263 M |
| Rolling stock | $351 M |
| Residual train control | $5.3 M |
| Charging microgrids | $7.5 M |
| EPC / project services | $140 M |
| **Total city programme** | **$2.14 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $441 M (20.6%) |
| Domestic / local capital | $1.70 bn (79.4%) |
| Annual public construction commitment | $197 M / yr for 7 years |
| Annual post-grace debt service | $162 M / yr |
| External capital saved vs default turnkey sensitivity | $3.40 bn |
| Capital + lifetime external interest saved | $7.67 bn |
| Annual OPEX | $56 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 875 assets / 4,913 tasks | [`arusha-operations-manifest.json`](operations/arusha-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`arusha.toml`](arusha.toml) | Expanded simulator scenario |
| [`arusha.corridor.geojson`](arusha.corridor.geojson) | GIS corridor and stations |
| [`arusha.design-quality.yaml`](arusha.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh arusha
```
