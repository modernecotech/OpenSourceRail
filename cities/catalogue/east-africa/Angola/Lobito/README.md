# Lobito — Urban Rail Network

**Country:** AO · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lobito-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.83 bn (88.4%) of external capital** and **$2.25 bn of external interest**. Capital plus saved interest totals **$4.09 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **8 lines**, including **5 additional residential lines**. **63.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **33.825 km to 43.526 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **45 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **222 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **222 light-metro-3car trainsets / 666 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Lobito rail network on OpenStreetMap](lobito-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 45 / 8 |
| Route length | 60.1 km double track |
| Direct transfers / reachable line pairs | 42.9% / 100.0% |
| Residents within 800 m radial station catchments | 129,408 (2020 raster; 50.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 222 × 3-car `light-metro-3car` trainsets (198 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 1,071,360 passenger-trips/day |
| Annual paid-trip planning range | 195.5–312.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.7 km | 12 | 64 | SW Outer ↔ N Mid |
| line-2 |  5.3 km | 6 | 25 | W Mid ↔ E Inner |
| line-3 |  5.7 km | 5 | 21 | S Inner ↔ W Mid |
| line-4 |  4.5 km | 4 | 18 | E Inner ↔ NE Mid |
| line-5 |  4.9 km | 4 | 19 | E Inner ↔ E Mid |
| line-6 |  6.9 km | 5 | 27 | E Inner ↔ N Mid |
| line-7 |  6.7 km | 5 | 25 | E Inner ↔ SE Outer |
| line-8 |  6.5 km | 4 | 23 | SW Inner ↔ SW Outer |
| **Total** | **60.1 km** | **45 unique** | **222** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,720 one-way journeys / 27,960 train-km/day |
| Annual traction demand | 132.3 GWh |
| Station/depot PV / storage | 49.3 MW / 351.0 MWh |
| Aggregate charging power | 39.0 MW |
| Dedicated solar plant | 7.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 6.9 km / 58 kWh |
| Lowest traversal charging margin | line-7: 86 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $520 M |
| Stations | $216 M |
| Depots | $125 M |
| Rolling stock | $200 M |
| Dedicated solar plant | $5.9 M |
| Residual train control | $3.0 M |
| Charging microgrids | $8.2 M |
| EPC / project services | $75 M |
| **Total city programme** | **$1.15 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $241 M (20.9%) |
| Domestic / local capital | $911 M (79.1%) |
| Annual public construction commitment | $131 M / yr for 5 years |
| Annual post-grace debt service | $100 M / yr |
| External capital saved vs default turnkey sensitivity | $1.83 bn |
| Capital + lifetime external interest saved | $4.09 bn |
| Annual OPEX | $33 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 492 assets / 2,794 tasks | [`lobito-operations-manifest.json`](operations/lobito-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lobito.toml`](lobito.toml) | Expanded simulator scenario |
| [`lobito.corridor.geojson`](lobito.corridor.geojson) | GIS corridor and stations |
| [`lobito.design-quality.yaml`](lobito.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lobito
```
