# Kakamega — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kakamega-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.04 bn (89.2%) of external capital** and **$2.55 bn of external interest**. Capital plus saved interest totals **$4.59 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **59.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **34.909 km to 48.269 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **56 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **201 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **201 tram-2car trainsets / 402 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kakamega rail network on OpenStreetMap](kakamega-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 56 / 16 |
| Route length | 75.6 km double track |
| Direct transfers / reachable line pairs | 27.3% / 100.0% |
| Residents within 800 m radial station catchments | 134,375 (2020 raster; 46.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 201 × 2-car `tram-2car` trainsets (174 peak revenue) |
| Peak network throughput | 105,600 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.6 km | 8 | 29 | W Outer ↔ E Mid |
| line-2 | 14.7 km | 10 | 36 | NE Outer ↔ W Mid |
| line-3 | 11.7 km | 9 | 30 | NW Mid ↔ S Outer |
| line-4 |  4.0 km | 4 | 13 | S Mid ↔ N Inner |
| line-5 |  9.3 km | 6 | 23 | E Inner ↔ W Mid |
| line-6 |  5.4 km | 4 | 14 | E Mid ↔ SE Outer |
| line-7 |  5.6 km | 4 | 15 | S Mid ↔ SW Outer |
| line-8 |  3.6 km | 3 | 11 | NE Mid ↔ N Mid |
| line-9 |  2.1 km | 3 | 10 | NW Mid ↔ NW Inner |
| line-10 |  4.3 km | 3 | 11 | S Outer ↔ SE Outer |
| line-11 |  3.1 km | 2 | 9 | NE Outer ↔ N Outer |
| **Total** | **75.6 km** | **56 unique** | **201** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 35,148 train-km/day |
| Annual traction demand | 110.8 GWh |
| Station/depot PV / storage | 66.7 MW / 459.5 MWh |
| Aggregate charging power | 25.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 5.6 km / 28 kWh |
| Lowest traversal charging margin | line-7: 18 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $609 M |
| Stations | $302 M |
| Depots | $152 M |
| Rolling stock | $113 M |
| Residual train control | $3.8 M |
| Charging microgrids | $5.2 M |
| EPC / project services | $83 M |
| **Total city programme** | **$1.27 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $245 M (19.4%) |
| Domestic / local capital | $1.02 bn (80.6%) |
| Annual public construction commitment | $134 M / yr for 7 years |
| Annual post-grace debt service | $111 M / yr |
| External capital saved vs default turnkey sensitivity | $2.04 bn |
| Capital + lifetime external interest saved | $4.59 bn |
| Annual OPEX | $34 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 529 assets / 2,791 tasks | [`kakamega-operations-manifest.json`](operations/kakamega-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kakamega.toml`](kakamega.toml) | Expanded simulator scenario |
| [`kakamega.corridor.geojson`](kakamega.corridor.geojson) | GIS corridor and stations |
| [`kakamega.design-quality.yaml`](kakamega.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kakamega
```
