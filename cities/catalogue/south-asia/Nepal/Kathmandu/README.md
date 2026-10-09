# Kathmandu — Urban Rail Network

**Country:** NP · **Population:** 1,442,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kathmandu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.87 bn (88.3%) of external capital** and **$7.35 bn of external interest**. Capital plus saved interest totals **$13.22 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **7 additional residential lines**. **80.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **147.692 km to 162.431 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **133 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **386 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **386 metro-4car trainsets / 1544 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kathmandu rail network on OpenStreetMap](kathmandu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 133 / 31 |
| Route length | 205.7 km double track |
| Direct transfers / reachable line pairs | 43.6% / 100.0% |
| Residents within 800 m radial station catchments | 4,783,434 (2020 raster; 63.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 386 × 4-car `metro-4car` trainsets (342 peak revenue) |
| Peak network throughput | 249,600 passengers/hour |
| Practical service capacity | 2,232,000 passenger-trips/day |
| Annual paid-trip planning range | 407.3–651.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.9 km | 21 | 68 | SE Outer ↔ NW Outer |
| line-2 | 24.9 km | 16 | 52 | SW Outer ↔ NE Mid |
| line-3 | 15.4 km | 11 | 38 | N Mid ↔ S Mid |
| line-4 | 20.5 km | 13 | 45 | N Mid ↔ SW Outer |
| line-5 | 25.9 km | 17 | 57 | E Outer ↔ W Outer |
| line-6 | 50.9 km | 27 | 26 | W Mid ↔ W Mid |
| line-7 |  8.6 km | 6 | 21 | E Mid ↔ N Inner |
| line-8 |  3.7 km | 3 | 11 | NW Inner ↔ SW Inner |
| line-9 |  7.6 km | 6 | 20 | NE Inner ↔ SE Mid |
| line-10 |  3.4 km | 3 | 11 | NE Mid ↔ N Inner |
| line-11 |  4.6 km | 4 | 14 | W Inner ↔ S Inner |
| line-12 |  4.3 km | 3 | 12 | E Inner ↔ E Mid |
| line-13 |  4.1 km | 3 | 11 | W Mid ↔ W Mid |
| **Total** | **205.7 km** | **133 unique** | **386** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,812 one-way journeys / 83,823 train-km/day |
| Annual traction demand | 528.7 GWh |
| Station/depot PV / storage | 95.6 MW / 673.0 MWh |
| Aggregate charging power | 172.5 MW |
| Dedicated solar plant | 286.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.7 km / 94 kWh |
| Lowest traversal charging margin | line-13: 103 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.82 bn |
| Stations | $718 M |
| Depots | $225 M |
| Rolling stock | $432 M |
| Dedicated solar plant | $229 M |
| Residual train control | $10 M |
| Charging microgrids | $35 M |
| EPC / project services | $227 M |
| **Total city programme** | **$3.69 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $780 M (21.1%) |
| Domestic / local capital | $2.91 bn (78.9%) |
| Annual public construction commitment | $293 M / yr for 7 years |
| Annual post-grace debt service | $238 M / yr |
| External capital saved vs default turnkey sensitivity | $5.87 bn |
| Capital + lifetime external interest saved | $13.22 bn |
| Annual OPEX | $86 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 20 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,116 assets / 5,813 tasks | [`kathmandu-operations-manifest.json`](operations/kathmandu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kathmandu.toml`](kathmandu.toml) | Expanded simulator scenario |
| [`kathmandu.corridor.geojson`](kathmandu.corridor.geojson) | GIS corridor and stations |
| [`kathmandu.design-quality.yaml`](kathmandu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kathmandu
```
