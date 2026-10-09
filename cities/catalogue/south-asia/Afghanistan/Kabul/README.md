# Kabul — Urban Rail Network

**Country:** AF · **Population:** 4,601,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kabul-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.53 bn (87.7%) of external capital** and **$12.31 bn of external interest**. Capital plus saved interest totals **$21.84 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **22 lines**, including **15 additional residential lines**. **80.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **194.539 km to 225.019 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **195 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**22 line-local depots** provide **653 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **653 metro-6car trainsets / 3918 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kabul rail network on OpenStreetMap](kabul-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 22 / 195 / 48 |
| Route length | 287.3 km double track |
| Direct transfers / reachable line pairs | 20.3% / 100.0% |
| Residents within 800 m radial station catchments | 2,551,725 (2020 raster; 61.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 653 × 6-car `metro-6car` trainsets (582 peak revenue) |
| Peak network throughput | 633,600 passengers/hour |
| Practical service capacity | 5,758,560 passenger-trips/day |
| Annual paid-trip planning range | 1050.9–1681.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.5 km | 18 | 67 | NE Outer ↔ W Mid |
| line-2 | 26.1 km | 16 | 62 | SE Mid ↔ NW Outer |
| line-3 | 18.5 km | 14 | 52 | W Mid ↔ NE Mid |
| line-4 | 26.0 km | 16 | 63 | SW Mid ↔ E Outer |
| line-5 | 29.1 km | 19 | 72 | NW Mid ↔ E Outer |
| line-6 | 18.5 km | 11 | 43 | E Outer ↔ NE Mid |
| line-7 | 53.0 km | 33 | 32 | NW Mid ↔ NW Mid |
| line-8 |  5.1 km | 4 | 16 | S Inner ↔ SE Inner |
| line-9 |  5.0 km | 5 | 18 | SW Mid ↔ SW Mid |
| line-10 |  4.9 km | 4 | 15 | NW Mid ↔ N Mid |
| line-11 |  5.4 km | 4 | 15 | W Mid ↔ W Mid |
| line-12 |  7.6 km | 6 | 21 | W Mid ↔ SW Inner |
| line-13 |  4.6 km | 3 | 13 | E Mid ↔ E Mid |
| line-14 |  5.0 km | 4 | 16 | SE Inner ↔ E Inner |
| line-15 |  3.9 km | 3 | 12 | W Mid ↔ SW Mid |
| line-16 |  4.5 km | 4 | 15 | S Mid ↔ SW Mid |
| line-17 | 10.0 km | 6 | 23 | W Mid ↔ W Mid |
| line-18 |  4.3 km | 5 | 17 | N Inner ↔ NW Inner |
| line-19 |  5.0 km | 3 | 13 | E Mid ↔ E Outer |
| line-20 | 11.6 km | 7 | 26 | S Mid ↔ SW Mid |
| line-21 |  6.1 km | 4 | 17 | NW Inner ↔ N Mid |
| line-22 |  9.6 km | 6 | 25 | NW Mid ↔ N Inner |
| **Total** | **287.3 km** | **195 unique** | **653** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 9,998 one-way journeys / 121,264 train-km/day |
| Annual traction demand | 1,147.3 GWh |
| Station/depot PV / storage | 156.5 MW / 1,190.0 MWh |
| Aggregate charging power | 354.0 MW |
| Dedicated solar plant | 403.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-20: 7.7 km / 112 kWh |
| Lowest traversal charging margin | line-19: 117 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.65 bn |
| Stations | $1.08 bn |
| Depots | $429 M |
| Rolling stock | $1.10 bn |
| Dedicated solar plant | $322 M |
| Residual train control | $14 M |
| Charging microgrids | $72 M |
| EPC / project services | $374 M |
| **Total city programme** | **$6.04 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.34 bn (22.2%) |
| Domestic / local capital | $4.70 bn (77.8%) |
| Annual public construction commitment | $831 M / yr for 10 years |
| Annual post-grace debt service | $763 M / yr |
| External capital saved vs default turnkey sensitivity | $9.53 bn |
| Capital + lifetime external interest saved | $21.84 bn |
| Annual OPEX | $141 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 40 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,751 assets / 9,345 tasks | [`kabul-operations-manifest.json`](operations/kabul-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kabul.toml`](kabul.toml) | Expanded simulator scenario |
| [`kabul.corridor.geojson`](kabul.corridor.geojson) | GIS corridor and stations |
| [`kabul.design-quality.yaml`](kabul.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kabul
```
