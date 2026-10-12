# Gulu — Urban Rail Network

**Country:** UG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gulu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.34 bn (88.2%) of external capital** and **$2.93 bn of external interest**. Capital plus saved interest totals **$5.26 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **5 lines**, including **2 additional residential lines**. **36.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **48.304 km to 63.357 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **48 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **261 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **261 light-metro-3car trainsets / 783 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Gulu rail network on OpenStreetMap](gulu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 48 / 5 |
| Route length | 73.9 km double track |
| Direct transfers / reachable line pairs | 50.0% / 100.0% |
| Residents within 800 m radial station catchments | 70,641 (2020 raster; 25.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 261 × 3-car `light-metro-3car` trainsets (234 peak revenue) |
| Peak network throughput | 72,000 passengers/hour |
| Practical service capacity | 669,600 passenger-trips/day |
| Annual paid-trip planning range | 122.2–195.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.8 km | 14 | 58 | SW Mid ↔ NE Mid |
| line-2 | 29.3 km | 16 | 100 | SE Outer ↔ NW Outer |
| line-3 | 16.4 km | 6 | 51 | W Outer ↔ NE Mid |
| line-4 |  5.2 km | 4 | 18 | S Inner ↔ SW Mid |
| line-5 |  8.1 km | 8 | 34 | SE Mid ↔ NE Inner |
| **Total** | **73.9 km** | **48 unique** | **261** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,325 one-way journeys / 34,342 train-km/day |
| Annual traction demand | 162.5 GWh |
| Station/depot PV / storage | 36.7 MW / 239.0 MWh |
| Aggregate charging power | 44.0 MW |
| Dedicated solar plant | 64.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.3 km / 70 kWh |
| Lowest traversal charging margin | line-4: 120 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $679 M |
| Stations | $303 M |
| Depots | $96 M |
| Rolling stock | $235 M |
| Dedicated solar plant | $52 M |
| Residual train control | $3.7 M |
| Charging microgrids | $9.1 M |
| EPC / project services | $93 M |
| **Total city programme** | **$1.47 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $311 M (21.2%) |
| Domestic / local capital | $1.16 bn (78.8%) |
| Annual public construction commitment | $177 M / yr for 7 years |
| Annual post-grace debt service | $150 M / yr |
| External capital saved vs default turnkey sensitivity | $2.34 bn |
| Capital + lifetime external interest saved | $5.26 bn |
| Annual OPEX | $36 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 548 assets / 3,222 tasks | [`gulu-operations-manifest.json`](operations/gulu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gulu.toml`](gulu.toml) | Expanded simulator scenario |
| [`gulu.corridor.geojson`](gulu.corridor.geojson) | GIS corridor and stations |
| [`gulu.design-quality.yaml`](gulu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gulu
```
