# Abha — Urban Rail Network

**Country:** SA · **Population:** 450,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Abha-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.80 bn (88.4%) of external capital** and **$3.45 bn of external interest**. Capital plus saved interest totals **$6.25 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **55.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **46.784 km to 70.360 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **64 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **348 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **348 light-metro-3car trainsets / 1044 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Abha rail network on OpenStreetMap](abha-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 64 / 9 |
| Route length | 101.6 km double track |
| Direct transfers / reachable line pairs | 22.2% / 46.7% |
| Residents within 800 m radial station catchments | 59,128 (2020 raster; 41.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 348 × 3-car `light-metro-3car` trainsets (311 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.5 km | 11 | 59 | E Mid ↔ W Outer |
| line-2 | 20.3 km | 11 | 69 | SE Mid ↔ W Outer |
| line-3 | 13.4 km | 8 | 43 | E Mid ↔ NW Mid |
| line-4 |  4.0 km | 3 | 16 | E Mid ↔ NE Outer |
| line-5 | 10.0 km | 7 | 32 | E Mid ↔ SW Inner |
| line-6 |  6.7 km | 4 | 24 | E Mid ↔ NE Outer |
| line-7 |  7.7 km | 5 | 27 | W Mid ↔ W Outer |
| line-8 |  7.1 km | 5 | 24 | NW Mid ↔ N Mid |
| line-9 |  6.5 km | 4 | 24 | E Mid ↔ SE Outer |
| line-10 |  8.3 km | 6 | 30 | SE Mid ↔ SW Mid |
| **Total** | **101.6 km** | **64 unique** | **348** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 47,258 train-km/day |
| Annual traction demand | 223.6 GWh |
| Station/depot PV / storage | 63.5 MW / 422.5 MWh |
| Aggregate charging power | 27.5 MW |
| Dedicated solar plant | 40.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 6.7 km / 48 kWh |
| Lowest traversal charging margin | line-4: 17 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $875 M |
| Stations | $250 M |
| Depots | $167 M |
| Rolling stock | $313 M |
| Dedicated solar plant | $32 M |
| Residual train control | $5.1 M |
| Charging microgrids | $5.7 M |
| EPC / project services | $113 M |
| **Total city programme** | **$1.76 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $369 M (21.0%) |
| Domestic / local capital | $1.39 bn (79.0%) |
| Annual public construction commitment | $122 M / yr for 5 years |
| Annual post-grace debt service | $85 M / yr |
| External capital saved vs default turnkey sensitivity | $2.80 bn |
| Capital + lifetime external interest saved | $6.25 bn |
| Annual OPEX | $111 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 25 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 733 assets / 4,271 tasks | [`abha-operations-manifest.json`](operations/abha-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`abha.toml`](abha.toml) | Expanded simulator scenario |
| [`abha.corridor.geojson`](abha.corridor.geojson) | GIS corridor and stations |
| [`abha.design-quality.yaml`](abha.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh abha
```
