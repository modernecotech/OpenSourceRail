# Kenitra — Urban Rail Network

**Country:** MA · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kenitra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.16 bn (88.1%) of external capital** and **$2.66 bn of external interest**. Capital plus saved interest totals **$4.83 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **85.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **48.553 km to 58.276 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **52 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **276 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **276 light-metro-3car trainsets / 828 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kenitra rail network on OpenStreetMap](kenitra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 52 / 8 |
| Route length | 78.3 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 413,928 (2020 raster; 69.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 276 × 3-car `light-metro-3car` trainsets (246 peak revenue) |
| Peak network throughput | 100,800 passengers/hour |
| Practical service capacity | 937,440 passenger-trips/day |
| Annual paid-trip planning range | 171.1–273.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.1 km | 9 | 49 | E Mid ↔ W Mid |
| line-2 | 16.7 km | 10 | 58 | SE Mid ↔ W Mid |
| line-3 | 19.9 km | 13 | 67 | SW Mid ↔ NE Outer |
| line-4 |  7.2 km | 6 | 27 | SE Mid ↔ SW Inner |
| line-5 |  2.9 km | 3 | 13 | NW Inner ↔ N Inner |
| line-6 | 10.3 km | 7 | 39 | W Mid ↔ SW Outer |
| line-7 |  6.1 km | 4 | 23 | E Inner ↔ NE Mid |
| **Total** | **78.3 km** | **52 unique** | **276** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 36,389 train-km/day |
| Annual traction demand | 172.1 GWh |
| Station/depot PV / storage | 45.8 MW / 298.0 MWh |
| Aggregate charging power | 21.5 MW |
| Dedicated solar plant | 45.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 8.9 km / 64 kWh |
| Lowest traversal charging margin | line-6: 41 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $638 M |
| Stations | $224 M |
| Depots | $121 M |
| Rolling stock | $248 M |
| Dedicated solar plant | $37 M |
| Residual train control | $3.9 M |
| Charging microgrids | $4.5 M |
| EPC / project services | $87 M |
| **Total city programme** | **$1.36 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $291 M (21.3%) |
| Domestic / local capital | $1.07 bn (78.7%) |
| Annual public construction commitment | $95 M / yr for 5 years |
| Annual post-grace debt service | $66 M / yr |
| External capital saved vs default turnkey sensitivity | $2.16 bn |
| Capital + lifetime external interest saved | $4.83 bn |
| Annual OPEX | $44 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 584 assets / 3,405 tasks | [`kenitra-operations-manifest.json`](operations/kenitra-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kenitra.toml`](kenitra.toml) | Expanded simulator scenario |
| [`kenitra.corridor.geojson`](kenitra.corridor.geojson) | GIS corridor and stations |
| [`kenitra.design-quality.yaml`](kenitra.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kenitra
```
