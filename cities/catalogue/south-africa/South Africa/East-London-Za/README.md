# East-London-Za — Urban Rail Network

**Country:** ZA · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only East-London-Za-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.72 bn (88.1%) of external capital** and **$3.35 bn of external interest**. Capital plus saved interest totals **$6.07 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **84.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **51.306 km to 64.699 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **62 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **316 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **316 light-metro-3car trainsets / 948 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![East-London-Za rail network on OpenStreetMap](east-london-za-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 62 / 11 |
| Route length | 93.9 km double track |
| Direct transfers / reachable line pairs | 26.7% / 100.0% |
| Residents within 800 m radial station catchments | 250,373 (2020 raster; 65.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 316 × 3-car `light-metro-3car` trainsets (282 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.5 km | 10 | 56 | E Outer ↔ S Outer |
| line-2 | 20.7 km | 12 | 65 | SE Outer ↔ NW Outer |
| line-3 | 21.0 km | 13 | 68 | NW Outer ↔ E Outer |
| line-4 |  4.9 km | 4 | 18 | S Inner ↔ SE Mid |
| line-5 |  3.6 km | 3 | 14 | NW Mid ↔ NW Outer |
| line-6 |  8.1 km | 6 | 27 | S Inner ↔ SE Mid |
| line-7 |  5.1 km | 4 | 19 | E Inner ↔ NE Mid |
| line-8 |  5.3 km | 4 | 19 | W Inner ↔ S Mid |
| line-9 |  3.7 km | 3 | 14 | NW Mid ↔ W Mid |
| line-10 |  4.1 km | 3 | 16 | NW Outer ↔ NW Outer |
| **Total** | **93.9 km** | **62 unique** | **316** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 43,656 train-km/day |
| Annual traction demand | 206.5 GWh |
| Station/depot PV / storage | 64.1 MW / 423.5 MWh |
| Aggregate charging power | 28.5 MW |
| Dedicated solar plant | 81.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-10: 4.1 km / 30 kWh |
| Lowest traversal charging margin | line-10: 16 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $804 M |
| Stations | $282 M |
| Depots | $161 M |
| Rolling stock | $284 M |
| Dedicated solar plant | $65 M |
| Residual train control | $4.7 M |
| Charging microgrids | $5.9 M |
| EPC / project services | $108 M |
| **Total city programme** | **$1.72 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $367 M (21.4%) |
| Domestic / local capital | $1.35 bn (78.6%) |
| Annual public construction commitment | $184 M / yr for 5 years |
| Annual post-grace debt service | $138 M / yr |
| External capital saved vs default turnkey sensitivity | $2.72 bn |
| Capital + lifetime external interest saved | $6.07 bn |
| Annual OPEX | $57 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 690 assets / 3,958 tasks | [`east-london-za-operations-manifest.json`](operations/east-london-za-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`east-london-za.toml`](east-london-za.toml) | Expanded simulator scenario |
| [`east-london-za.corridor.geojson`](east-london-za.corridor.geojson) | GIS corridor and stations |
| [`east-london-za.design-quality.yaml`](east-london-za.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh east-london-za
```
