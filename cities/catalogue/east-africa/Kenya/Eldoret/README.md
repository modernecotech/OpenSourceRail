# Eldoret — Urban Rail Network

**Country:** KE · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Eldoret-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.42 bn (88.5%) of external capital** and **$4.29 bn of external interest**. Capital plus saved interest totals **$7.70 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **16 lines**, including **13 additional residential lines**. **75.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **45.978 km to 96.219 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **79 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**16 line-local depots** provide **400 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **400 light-metro-3car trainsets / 1200 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Eldoret rail network on OpenStreetMap](eldoret-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 16 / 79 / 18 |
| Route length | 109.3 km double track |
| Direct transfers / reachable line pairs | 19.2% / 100.0% |
| Residents within 800 m radial station catchments | 326,075 (2020 raster; 61.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 400 × 3-car `light-metro-3car` trainsets (353 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,142,720 passenger-trips/day |
| Annual paid-trip planning range | 391.0–625.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.3 km | 14 | 71 | SE Mid ↔ NW Outer |
| line-2 | 13.8 km | 11 | 47 | E Mid ↔ SW Mid |
| line-3 | 21.0 km | 14 | 72 | NW Outer ↔ SE Mid |
| line-4 |  4.9 km | 4 | 18 | SW Inner ↔ S Mid |
| line-5 |  2.2 km | 3 | 13 | NW Inner ↔ N Inner |
| line-6 |  4.8 km | 4 | 19 | E Inner ↔ NE Mid |
| line-7 |  2.1 km | 2 | 10 | SE Inner ↔ E Inner |
| line-8 |  4.9 km | 3 | 17 | SE Mid ↔ S Mid |
| line-9 |  2.5 km | 2 | 11 | NW Mid ↔ N Mid |
| line-10 |  3.4 km | 3 | 14 | SW Inner ↔ W Inner |
| line-11 |  2.7 km | 2 | 11 | NW Mid ↔ W Inner |
| line-12 |  6.2 km | 3 | 21 | E Mid ↔ NE Mid |
| line-13 |  8.7 km | 5 | 29 | SE Mid ↔ S Mid |
| line-14 |  6.5 km | 4 | 23 | E Mid ↔ SE Mid |
| line-15 |  3.1 km | 3 | 14 | E Mid ↔ NE Mid |
| line-16 |  2.0 km | 2 | 10 | SW Inner ↔ SW Inner |
| **Total** | **109.3 km** | **79 unique** | **400** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 7,440 one-way journeys / 50,835 train-km/day |
| Annual traction demand | 240.5 GWh |
| Station/depot PV / storage | 95.0 MW / 690.0 MWh |
| Aggregate charging power | 66.0 MW |
| Dedicated solar plant | 7.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 8.8 km / 74 kWh |
| Lowest traversal charging margin | line-11: 73 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.01 bn |
| Stations | $366 M |
| Depots | $242 M |
| Rolling stock | $360 M |
| Dedicated solar plant | $5.8 M |
| Residual train control | $5.5 M |
| Charging microgrids | $14 M |
| EPC / project services | $140 M |
| **Total city programme** | **$2.15 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $443 M (20.7%) |
| Domestic / local capital | $1.70 bn (79.3%) |
| Annual public construction commitment | $225 M / yr for 7 years |
| Annual post-grace debt service | $187 M / yr |
| External capital saved vs default turnkey sensitivity | $3.42 bn |
| Capital + lifetime external interest saved | $7.70 bn |
| Annual OPEX | $60 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 875 assets / 4,982 tasks | [`eldoret-operations-manifest.json`](operations/eldoret-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`eldoret.toml`](eldoret.toml) | Expanded simulator scenario |
| [`eldoret.corridor.geojson`](eldoret.corridor.geojson) | GIS corridor and stations |
| [`eldoret.design-quality.yaml`](eldoret.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh eldoret
```
