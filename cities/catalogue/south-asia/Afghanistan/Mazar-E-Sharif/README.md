# Mazar-E-Sharif — Urban Rail Network

**Country:** AF · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mazar-E-Sharif-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.09 bn (88.4%) of external capital** and **$2.70 bn of external interest**. Capital plus saved interest totals **$4.79 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **3 additional residential lines**. **77.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **49.411 km to 54.467 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **50 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **252 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **252 light-metro-3car trainsets / 756 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mazar-E-Sharif rail network on OpenStreetMap](mazar-e-sharif-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 50 / 8 |
| Route length | 68.8 km double track |
| Direct transfers / reachable line pairs | 40.0% / 100.0% |
| Residents within 800 m radial station catchments | 283,322 (2020 raster; 61.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 252 × 3-car `light-metro-3car` trainsets (225 peak revenue) |
| Peak network throughput | 86,400 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.2 km | 7 | 45 | NE Outer ↔ NW Mid |
| line-2 | 24.2 km | 17 | 87 | E Outer ↔ SW Outer |
| line-3 | 19.8 km | 15 | 70 | SW Outer ↔ NE Outer |
| line-4 |  3.3 km | 3 | 14 | E Inner ↔ NW Inner |
| line-5 |  2.1 km | 2 | 10 | NE Mid ↔ E Mid |
| line-6 |  6.3 km | 6 | 26 | E Inner ↔ SW Inner |
| **Total** | **68.8 km** | **50 unique** | **252** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,790 one-way journeys / 32,011 train-km/day |
| Annual traction demand | 151.4 GWh |
| Station/depot PV / storage | 41.1 MW / 258.5 MWh |
| Aggregate charging power | 21.5 MW |
| Dedicated solar plant | 29.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.4 km / 46 kWh |
| Lowest traversal charging margin | line-5: 33 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $607 M |
| Stations | $259 M |
| Depots | $106 M |
| Rolling stock | $227 M |
| Dedicated solar plant | $24 M |
| Residual train control | $3.4 M |
| Charging microgrids | $4.5 M |
| EPC / project services | $84 M |
| **Total city programme** | **$1.32 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $276 M (21.0%) |
| Domestic / local capital | $1.04 bn (79.0%) |
| Annual public construction commitment | $183 M / yr for 10 years |
| Annual post-grace debt service | $168 M / yr |
| External capital saved vs default turnkey sensitivity | $2.09 bn |
| Capital + lifetime external interest saved | $4.79 bn |
| Annual OPEX | $31 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 546 assets / 3,160 tasks | [`mazar-e-sharif-operations-manifest.json`](operations/mazar-e-sharif-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mazar-e-sharif.toml`](mazar-e-sharif.toml) | Expanded simulator scenario |
| [`mazar-e-sharif.corridor.geojson`](mazar-e-sharif.corridor.geojson) | GIS corridor and stations |
| [`mazar-e-sharif.design-quality.yaml`](mazar-e-sharif.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mazar-e-sharif
```
