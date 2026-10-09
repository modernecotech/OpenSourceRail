# Vientiane — Urban Rail Network

**Country:** LA · **Population:** 948,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Vientiane-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.78 bn (88.3%) of external capital** and **$4.74 bn of external interest**. Capital plus saved interest totals **$8.52 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **16 lines**, including **13 additional residential lines**. **70.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **61.024 km to 93.931 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **83 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**16 line-local depots** provide **442 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **442 light-metro-3car trainsets / 1326 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Vientiane rail network on OpenStreetMap](vientiane-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 16 / 83 / 18 |
| Route length | 124.0 km double track |
| Direct transfers / reachable line pairs | 18.3% / 100.0% |
| Residents within 800 m radial station catchments | 315,838 (2020 raster; 53.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 442 × 3-car `light-metro-3car` trainsets (391 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,142,720 passenger-trips/day |
| Annual paid-trip planning range | 391.0–625.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.9 km | 12 | 63 | NE Outer ↔ S Mid |
| line-2 | 19.1 km | 12 | 64 | NE Outer ↔ SW Mid |
| line-3 | 25.1 km | 17 | 83 | NW Outer ↔ SE Outer |
| line-4 |  2.9 km | 2 | 11 | SE Inner ↔ S Inner |
| line-5 |  6.0 km | 3 | 20 | SW Inner ↔ W Outer |
| line-6 |  5.8 km | 4 | 19 | SE Inner ↔ NE Mid |
| line-7 |  2.7 km | 3 | 13 | S Mid ↔ S Mid |
| line-8 |  9.7 km | 6 | 35 | SW Inner ↔ W Outer |
| line-9 |  2.8 km | 2 | 11 | SE Mid ↔ SE Inner |
| line-10 | 13.3 km | 7 | 46 | E Mid ↔ S Mid |
| line-11 |  4.6 km | 3 | 17 | N Inner ↔ N Mid |
| line-12 |  2.1 km | 2 | 10 | S Inner ↔ W Inner |
| line-13 |  2.6 km | 2 | 11 | NE Mid ↔ N Mid |
| line-14 |  3.8 km | 3 | 15 | NW Outer ↔ W Outer |
| line-15 |  3.3 km | 3 | 14 | S Mid ↔ S Inner |
| line-16 |  2.2 km | 2 | 10 | SE Mid ↔ SE Mid |
| **Total** | **124.0 km** | **83 unique** | **442** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 7,440 one-way journeys / 57,662 train-km/day |
| Annual traction demand | 272.8 GWh |
| Station/depot PV / storage | 98.3 MW / 670.5 MWh |
| Aggregate charging power | 38.5 MW |
| Dedicated solar plant | 66.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-10: 4.6 km / 35 kWh |
| Lowest traversal charging margin | line-14: 18 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.10 bn |
| Stations | $409 M |
| Depots | $249 M |
| Rolling stock | $398 M |
| Dedicated solar plant | $53 M |
| Residual train control | $6.2 M |
| Charging microgrids | $8.0 M |
| EPC / project services | $152 M |
| **Total city programme** | **$2.38 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $502 M (21.1%) |
| Domestic / local capital | $1.88 bn (78.9%) |
| Annual public construction commitment | $234 M / yr for 7 years |
| Annual post-grace debt service | $193 M / yr |
| External capital saved vs default turnkey sensitivity | $3.78 bn |
| Capital + lifetime external interest saved | $8.52 bn |
| Annual OPEX | $63 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 951 assets / 5,467 tasks | [`vientiane-operations-manifest.json`](operations/vientiane-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`vientiane.toml`](vientiane.toml) | Expanded simulator scenario |
| [`vientiane.corridor.geojson`](vientiane.corridor.geojson) | GIS corridor and stations |
| [`vientiane.design-quality.yaml`](vientiane.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh vientiane
```
