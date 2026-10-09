# Medina — Urban Rail Network

**Country:** SA · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Medina-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$10.01 bn (88.5%) of external capital** and **$12.30 bn of external interest**. Capital plus saved interest totals **$22.31 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **35 lines**, including **29 additional residential lines**. **80.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **148.772 km to 225.804 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **230 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**35 line-local depots** provide **725 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **725 metro-4car trainsets / 2900 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Medina rail network on OpenStreetMap](medina-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 35 / 230 / 59 |
| Route length | 345.0 km double track |
| Direct transfers / reachable line pairs | 11.4% / 100.0% |
| Residents within 800 m radial station catchments | 760,181 (2020 raster; 60.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 725 × 4-car `metro-4car` trainsets (636 peak revenue) |
| Peak network throughput | 672,000 passengers/hour |
| Practical service capacity | 6,160,320 passenger-trips/day |
| Annual paid-trip planning range | 1124.3–1798.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.7 km | 23 | 75 | NW Outer ↔ SE Outer |
| line-2 | 19.1 km | 11 | 41 | SW Mid ↔ NE Mid |
| line-3 | 18.6 km | 12 | 42 | NW Mid ↔ S Mid |
| line-4 | 23.8 km | 12 | 46 | NE Outer ↔ W Outer |
| line-5 | 19.4 km | 12 | 43 | NW Mid ↔ E Outer |
| line-6 | 58.5 km | 32 | 30 | NE Mid ↔ NE Mid |
| line-7 |  5.3 km | 3 | 13 | E Mid ↔ E Inner |
| line-8 |  4.8 km | 4 | 13 | S Mid ↔ SW Mid |
| line-9 |  3.7 km | 3 | 11 | E Mid ↔ E Inner |
| line-10 |  4.1 km | 4 | 14 | SE Inner ↔ SW Inner |
| line-11 |  5.4 km | 4 | 13 | SE Mid ↔ SE Mid |
| line-12 |  5.2 km | 3 | 12 | W Mid ↔ SW Outer |
| line-13 |  4.8 km | 3 | 11 | E Mid ↔ NE Outer |
| line-14 |  4.5 km | 3 | 11 | SE Mid ↔ S Mid |
| line-15 |  7.4 km | 6 | 18 | SW Mid ↔ SW Outer |
| line-16 |  5.1 km | 4 | 14 | N Mid ↔ N Outer |
| line-17 |  5.1 km | 5 | 17 | NW Inner ↔ SW Inner |
| line-18 |  4.3 km | 4 | 13 | SW Mid ↔ SW Mid |
| line-19 |  6.1 km | 4 | 14 | E Mid ↔ E Outer |
| line-20 |  3.5 km | 3 | 11 | S Mid ↔ S Outer |
| line-21 |  5.1 km | 4 | 15 | N Inner ↔ SE Inner |
| line-22 |  5.4 km | 5 | 17 | N Inner ↔ NW Inner |
| line-23 |  5.0 km | 4 | 14 | SW Mid ↔ SW Outer |
| line-24 | 12.7 km | 8 | 27 | E Mid ↔ SE Outer |
| line-25 | 10.9 km | 6 | 23 | E Outer ↔ NE Outer |
| line-26 |  5.3 km | 4 | 15 | W Mid ↔ W Mid |
| line-27 | 13.9 km | 10 | 30 | SW Mid ↔ S Mid |
| line-28 |  4.4 km | 4 | 13 | E Outer ↔ E Outer |
| line-29 |  5.1 km | 4 | 14 | S Mid ↔ SE Outer |
| line-30 |  6.4 km | 4 | 15 | E Mid ↔ SE Inner |
| line-31 |  4.2 km | 3 | 12 | NE Mid ↔ E Inner |
| line-32 |  6.8 km | 5 | 18 | N Mid ↔ N Outer |
| line-33 |  9.4 km | 8 | 27 | W Outer ↔ W Inner |
| line-34 |  5.2 km | 3 | 12 | SW Inner ↔ SW Mid |
| line-35 |  3.8 km | 3 | 11 | NE Mid ↔ NE Outer |
| **Total** | **345.0 km** | **230 unique** | **725** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 16,042 one-way journeys / 146,794 train-km/day |
| Annual traction demand | 925.9 GWh |
| Station/depot PV / storage | 223.3 MW / 1,641.5 MWh |
| Aggregate charging power | 294.0 MW |
| Dedicated solar plant | 229.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-25: 10.9 km / 117 kWh |
| Lowest traversal charging margin | line-25: 43 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.00 bn |
| Stations | $1.26 bn |
| Depots | $544 M |
| Rolling stock | $812 M |
| Dedicated solar plant | $184 M |
| Residual train control | $17 M |
| Charging microgrids | $61 M |
| EPC / project services | $399 M |
| **Total city programme** | **$6.28 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.30 bn (20.7%) |
| Domestic / local capital | $4.98 bn (79.3%) |
| Annual public construction commitment | $437 M / yr for 5 years |
| Annual post-grace debt service | $303 M / yr |
| External capital saved vs default turnkey sensitivity | $10.01 bn |
| Capital + lifetime external interest saved | $22.31 bn |
| Annual OPEX | $358 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 32 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,019 assets / 10,531 tasks | [`medina-operations-manifest.json`](operations/medina-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`medina.toml`](medina.toml) | Expanded simulator scenario |
| [`medina.corridor.geojson`](medina.corridor.geojson) | GIS corridor and stations |
| [`medina.design-quality.yaml`](medina.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh medina
```
