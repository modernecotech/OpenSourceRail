# Thika — Urban Rail Network

**Country:** KE · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Thika-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.85 bn (88.0%) of external capital** and **$4.82 bn of external interest**. Capital plus saved interest totals **$8.67 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **15 lines**, including **12 additional residential lines**. **65.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **53.545 km to 76.181 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **88 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**15 line-local depots** provide **490 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **490 light-metro-3car trainsets / 1470 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Thika rail network on OpenStreetMap](thika-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 15 / 88 / 18 |
| Route length | 134.8 km double track |
| Direct transfers / reachable line pairs | 17.1% / 100.0% |
| Residents within 800 m radial station catchments | 189,950 (2020 raster; 50.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 490 × 3-car `light-metro-3car` trainsets (435 peak revenue) |
| Peak network throughput | 216,000 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.1 km | 16 | 91 | SW Mid ↔ NE Outer |
| line-2 | 18.3 km | 12 | 61 | E Mid ↔ W Mid |
| line-3 | 23.8 km | 14 | 81 | SW Outer ↔ NE Mid |
| line-4 |  2.3 km | 2 | 10 | SE Mid ↔ SE Mid |
| line-5 |  5.3 km | 4 | 19 | S Inner ↔ E Inner |
| line-6 |  2.5 km | 2 | 11 | SW Mid ↔ SW Mid |
| line-7 |  3.0 km | 3 | 14 | E Mid ↔ E Outer |
| line-8 |  2.9 km | 2 | 11 | SE Mid ↔ SE Mid |
| line-9 |  4.6 km | 4 | 18 | SW Outer ↔ SW Outer |
| line-10 |  2.6 km | 2 | 11 | NE Outer ↔ N Outer |
| line-11 | 13.6 km | 8 | 50 | NE Mid ↔ NW Outer |
| line-12 |  3.1 km | 2 | 12 | S Inner ↔ SE Mid |
| line-13 | 12.3 km | 8 | 47 | W Mid ↔ NW Outer |
| line-14 |  2.2 km | 3 | 13 | W Inner ↔ SW Inner |
| line-15 | 12.1 km | 6 | 41 | NE Outer ↔ E Mid |
| **Total** | **134.8 km** | **88 unique** | **490** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,975 one-way journeys / 62,699 train-km/day |
| Annual traction demand | 296.6 GWh |
| Station/depot PV / storage | 90.0 MW / 650.0 MWh |
| Aggregate charging power | 65.0 MW |
| Dedicated solar plant | 91.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-11: 13.6 km / 102 kWh |
| Lowest traversal charging margin | line-12: 72 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.10 bn |
| Stations | $398 M |
| Depots | $245 M |
| Rolling stock | $441 M |
| Dedicated solar plant | $73 M |
| Residual train control | $6.7 M |
| Charging microgrids | $14 M |
| EPC / project services | $154 M |
| **Total city programme** | **$2.43 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $525 M (21.6%) |
| Domestic / local capital | $1.90 bn (78.4%) |
| Annual public construction commitment | $253 M / yr for 7 years |
| Annual post-grace debt service | $211 M / yr |
| External capital saved vs default turnkey sensitivity | $3.85 bn |
| Capital + lifetime external interest saved | $8.67 bn |
| Annual OPEX | $67 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,012 assets / 5,931 tasks | [`thika-operations-manifest.json`](operations/thika-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`thika.toml`](thika.toml) | Expanded simulator scenario |
| [`thika.corridor.geojson`](thika.corridor.geojson) | GIS corridor and stations |
| [`thika.design-quality.yaml`](thika.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh thika
```
