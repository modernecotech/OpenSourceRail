# Galle — Urban Rail Network

**Country:** LK · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Galle-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.34 bn (88.1%) of external capital** and **$4.19 bn of external interest**. Capital plus saved interest totals **$7.53 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **15 lines**, including **12 additional residential lines**. **74.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **49.775 km to 80.305 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **78 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**15 line-local depots** provide **415 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **415 light-metro-3car trainsets / 1245 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Galle rail network on OpenStreetMap](galle-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 15 / 78 / 17 |
| Route length | 116.9 km double track |
| Direct transfers / reachable line pairs | 16.2% / 100.0% |
| Residents within 800 m radial station catchments | 240,790 (2020 raster; 60.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 415 × 3-car `light-metro-3car` trainsets (368 peak revenue) |
| Peak network throughput | 216,000 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.3 km | 15 | 78 | SE Outer ↔ W Mid |
| line-2 | 19.0 km | 11 | 64 | NW Mid ↔ SE Outer |
| line-3 | 16.2 km | 11 | 53 | NE Outer ↔ SW Inner |
| line-4 |  4.6 km | 3 | 17 | NW Inner ↔ N Inner |
| line-5 |  2.5 km | 2 | 11 | E Inner ↔ SE Inner |
| line-6 |  4.2 km | 3 | 15 | NW Mid ↔ W Inner |
| line-7 |  2.6 km | 2 | 11 | SE Mid ↔ E Mid |
| line-8 |  6.7 km | 5 | 27 | W Mid ↔ NW Outer |
| line-9 |  3.9 km | 3 | 14 | SW Inner ↔ W Mid |
| line-10 |  8.7 km | 5 | 30 | NW Inner ↔ N Mid |
| line-11 |  8.6 km | 6 | 32 | NW Mid ↔ NW Outer |
| line-12 |  4.3 km | 3 | 16 | SE Mid ↔ SE Mid |
| line-13 |  2.5 km | 2 | 10 | E Inner ↔ E Inner |
| line-14 |  7.5 km | 5 | 27 | S Inner ↔ SE Mid |
| line-15 |  2.3 km | 2 | 10 | SE Outer ↔ E Outer |
| **Total** | **116.9 km** | **78 unique** | **415** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,975 one-way journeys / 54,361 train-km/day |
| Annual traction demand | 257.1 GWh |
| Station/depot PV / storage | 89.7 MW / 624.5 MWh |
| Aggregate charging power | 32.0 MW |
| Dedicated solar plant | 65.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-11: 8.6 km / 64 kWh |
| Lowest traversal charging margin | line-12: 14 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $957 M |
| Stations | $341 M |
| Depots | $234 M |
| Rolling stock | $374 M |
| Dedicated solar plant | $53 M |
| Residual train control | $5.8 M |
| Charging microgrids | $6.6 M |
| EPC / project services | $134 M |
| **Total city programme** | **$2.11 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $451 M (21.4%) |
| Domestic / local capital | $1.66 bn (78.6%) |
| Annual public construction commitment | $246 M / yr for 7 years |
| Annual post-grace debt service | $208 M / yr |
| External capital saved vs default turnkey sensitivity | $3.34 bn |
| Capital + lifetime external interest saved | $7.53 bn |
| Annual OPEX | $59 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 885 assets / 5,101 tasks | [`galle-operations-manifest.json`](operations/galle-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`galle.toml`](galle.toml) | Expanded simulator scenario |
| [`galle.corridor.geojson`](galle.corridor.geojson) | GIS corridor and stations |
| [`galle.design-quality.yaml`](galle.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh galle
```
