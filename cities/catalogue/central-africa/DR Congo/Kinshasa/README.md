# Kinshasa — Urban Rail Network

**Country:** CD · **Population:** 17,178,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kinshasa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$26.53 bn (87.4%) of external capital** and **$34.27 bn of external interest**. Capital plus saved interest totals **$60.80 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **54.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **323.681 km to 524.562 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **617 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **1775 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **1775 metro-6car trainsets / 10650 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kinshasa rail network on OpenStreetMap](kinshasa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 617 / 101 |
| Route length | 639.8 km double track |
| Direct transfers / reachable line pairs | 46.2% / 100.0% |
| Residents within 800 m radial station catchments | 3,036,815 (2020 raster; 40.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 1775 × 6-car `metro-6car` trainsets (1605 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 62.6 km | 85 | 265 | N Mid ↔ SE Outer |
| line-2 | 71.5 km | 86 | 276 | E Outer ↔ N Mid |
| line-3 | 31.8 km | 29 | 101 | SE Mid ↔ W Mid |
| line-4 | 61.7 km | 72 | 233 | S Mid ↔ N Mid |
| line-5 | 55.1 km | 60 | 193 | SW Outer ↔ E Outer |
| line-6 | 70.0 km | 40 | 158 | SE Mid ↔ NW Outer |
| line-7 | 91.8 km | 87 | 294 | NE Outer ↔ S Outer |
| line-8 | 36.7 km | 16 | 73 | E Mid ↔ W Outer |
| line-9 | 125.5 km | 128 | 107 | NW Inner ↔ NW Inner |
| line-10 |  6.4 km | 3 | 15 | SE Inner ↔ SE Mid |
| line-11 |  6.5 km | 3 | 15 | E Outer ↔ SE Outer |
| line-12 |  6.5 km | 2 | 14 | E Mid ↔ E Mid |
| line-13 |  7.4 km | 4 | 18 | SE Mid ↔ SE Outer |
| line-14 |  6.3 km | 2 | 13 | E Outer ↔ SE Outer |
| **Total** | **639.8 km** | **617 unique** | **1775** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 268,356 train-km/day |
| Annual traction demand | 2,538.9 GWh |
| Station/depot PV / storage | 248.5 MW / 1,750.0 MWh |
| Aggregate charging power | 1,218.0 MW |
| Dedicated solar plant | 1,380.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 20.9 km / 313 kWh |
| Lowest traversal charging margin | line-12: 88 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $6.14 bn |
| Stations | $4.71 bn |
| Depots | $623 M |
| Rolling stock | $2.98 bn |
| Dedicated solar plant | $1.10 bn |
| Residual train control | $32 M |
| Charging microgrids | $245 M |
| EPC / project services | $1.03 bn |
| **Total city programme** | **$16.87 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.83 bn (22.7%) |
| Domestic / local capital | $13.04 bn (77.3%) |
| Annual public construction commitment | $1.79 bn / yr for 10 years |
| Annual post-grace debt service | $1.63 bn / yr |
| External capital saved vs default turnkey sensitivity | $26.53 bn |
| Capital + lifetime external interest saved | $60.80 bn |
| Annual OPEX | $395 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 5,146 assets / 27,272 tasks | [`kinshasa-operations-manifest.json`](operations/kinshasa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kinshasa.toml`](kinshasa.toml) | Expanded simulator scenario |
| [`kinshasa.corridor.geojson`](kinshasa.corridor.geojson) | GIS corridor and stations |
| [`kinshasa.design-quality.yaml`](kinshasa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kinshasa
```
