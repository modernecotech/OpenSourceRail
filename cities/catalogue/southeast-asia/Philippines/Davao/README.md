# Davao — Urban Rail Network

**Country:** PH · **Population:** 1,827,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Davao-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.74 bn (88.2%) of external capital** and **$10.74 bn of external interest**. Capital plus saved interest totals **$19.48 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **15 lines**, including **9 additional residential lines**. **82.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **179.279 km to 204.026 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **209 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**15 line-local depots** provide **593 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **593 metro-4car trainsets / 2372 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Davao rail network on OpenStreetMap](davao-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 15 / 209 / 45 |
| Route length | 331.9 km double track |
| Direct transfers / reachable line pairs | 37.1% / 100.0% |
| Residents within 800 m radial station catchments | 1,061,410 (2020 raster; 66.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 593 × 4-car `metro-4car` trainsets (532 peak revenue) |
| Peak network throughput | 288,000 passengers/hour |
| Practical service capacity | 2,589,120 passenger-trips/day |
| Annual paid-trip planning range | 472.5–756.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 44.1 km | 24 | 87 | NE Outer ↔ SW Outer |
| line-2 | 37.7 km | 26 | 84 | NW Outer ↔ SE Mid |
| line-3 | 39.9 km | 22 | 79 | E Outer ↔ W Outer |
| line-4 | 33.5 km | 22 | 74 | W Mid ↔ E Outer |
| line-5 | 29.2 km | 18 | 62 | NW Outer ↔ SE Mid |
| line-6 | 85.7 km | 53 | 47 | NW Mid ↔ NW Mid |
| line-7 |  5.5 km | 4 | 15 | S Mid ↔ SE Mid |
| line-8 |  5.9 km | 4 | 15 | S Mid ↔ SW Mid |
| line-9 |  6.1 km | 4 | 15 | NE Mid ↔ E Mid |
| line-10 |  7.2 km | 6 | 20 | E Mid ↔ SE Mid |
| line-11 |  5.9 km | 4 | 15 | SW Mid ↔ SW Outer |
| line-12 |  6.6 km | 5 | 18 | E Mid ↔ NE Inner |
| line-13 |  6.7 km | 5 | 18 | S Mid ↔ SW Mid |
| line-14 |  5.6 km | 4 | 15 | SE Inner ↔ E Mid |
| line-15 | 12.1 km | 8 | 29 | E Mid ↔ NE Outer |
| **Total** | **331.9 km** | **209 unique** | **593** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,742 one-way journeys / 134,382 train-km/day |
| Annual traction demand | 847.6 GWh |
| Station/depot PV / storage | 127.8 MW / 864.0 MWh |
| Aggregate charging power | 286.5 MW |
| Dedicated solar plant | 409.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.4 km / 104 kWh |
| Lowest traversal charging margin | line-9: 178 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.61 bn |
| Stations | $1.20 bn |
| Depots | $290 M |
| Rolling stock | $664 M |
| Dedicated solar plant | $327 M |
| Residual train control | $17 M |
| Charging microgrids | $60 M |
| EPC / project services | $338 M |
| **Total city programme** | **$5.50 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.17 bn (21.2%) |
| Domestic / local capital | $4.33 bn (78.8%) |
| Annual public construction commitment | $441 M / yr for 5 years |
| Annual post-grace debt service | $312 M / yr |
| External capital saved vs default turnkey sensitivity | $8.74 bn |
| Capital + lifetime external interest saved | $19.48 bn |
| Annual OPEX | $151 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 68 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,738 assets / 9,069 tasks | [`davao-operations-manifest.json`](operations/davao-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`davao.toml`](davao.toml) | Expanded simulator scenario |
| [`davao.corridor.geojson`](davao.corridor.geojson) | GIS corridor and stations |
| [`davao.design-quality.yaml`](davao.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh davao
```
