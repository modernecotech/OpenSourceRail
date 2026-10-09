# Kananga — Urban Rail Network

**Country:** CD · **Population:** 1,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kananga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.27 bn (88.7%) of external capital** and **$2.94 bn of external interest**. Capital plus saved interest totals **$5.21 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **8 additional residential lines**. **34.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **37.401 km to 72.994 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **51 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **149 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **149 metro-4car trainsets / 596 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kananga rail network on OpenStreetMap](kananga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 51 / 12 |
| Route length | 74.1 km double track |
| Direct transfers / reachable line pairs | 24.4% / 100.0% |
| Residents within 800 m radial station catchments | 456,571 (2020 raster; 26.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 149 × 4-car `metro-4car` trainsets (128 peak revenue) |
| Peak network throughput | 192,000 passengers/hour |
| Practical service capacity | 1,696,320 passenger-trips/day |
| Annual paid-trip planning range | 309.6–495.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.6 km | 8 | 29 | S Outer ↔ NW Mid |
| line-2 | 24.1 km | 13 | 13 | NW Inner ↔ NW Mid |
| line-3 |  2.3 km | 3 | 10 | W Mid ↔ W Outer |
| line-4 |  5.4 km | 4 | 15 | N Inner ↔ NW Mid |
| line-5 |  4.3 km | 3 | 12 | W Mid ↔ NW Outer |
| line-6 |  4.6 km | 4 | 13 | E Mid ↔ NE Outer |
| line-7 |  6.5 km | 6 | 20 | W Mid ↔ W Inner |
| line-8 |  4.5 km | 3 | 11 | S Outer ↔ SE Outer |
| line-9 |  6.3 km | 4 | 15 | E Mid ↔ SE Outer |
| line-10 |  3.6 km | 3 | 11 | NE Mid ↔ NE Outer |
| **Total** | **74.1 km** | **51 unique** | **149** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,418 one-way journeys / 28,856 train-km/day |
| Annual traction demand | 182.0 GWh |
| Station/depot PV / storage | 61.4 MW / 457.0 MWh |
| Aggregate charging power | 72.0 MW |
| Dedicated solar plant | 48.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 4.5 km / 45 kWh |
| Lowest traversal charging margin | line-8: 98 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $722 M |
| Stations | $243 M |
| Depots | $144 M |
| Rolling stock | $167 M |
| Dedicated solar plant | $39 M |
| Residual train control | $3.7 M |
| Charging microgrids | $15 M |
| EPC / project services | $91 M |
| **Total city programme** | **$1.42 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $290 M (20.4%) |
| Domestic / local capital | $1.13 bn (79.6%) |
| Annual public construction commitment | $154 M / yr for 10 years |
| Annual post-grace debt service | $139 M / yr |
| External capital saved vs default turnkey sensitivity | $2.27 bn |
| Capital + lifetime external interest saved | $5.21 bn |
| Annual OPEX | $33 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 443 assets / 2,238 tasks | [`kananga-operations-manifest.json`](operations/kananga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kananga.toml`](kananga.toml) | Expanded simulator scenario |
| [`kananga.corridor.geojson`](kananga.corridor.geojson) | GIS corridor and stations |
| [`kananga.design-quality.yaml`](kananga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kananga
```
