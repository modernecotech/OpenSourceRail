# Hofuf — Urban Rail Network

**Country:** SA · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hofuf-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.14 bn (88.3%) of external capital** and **$5.09 bn of external interest**. Capital plus saved interest totals **$9.22 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **19 lines**, including **16 additional residential lines**. **71.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **53.388 km to 89.810 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **98 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**19 line-local depots** provide **503 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **503 light-metro-3car trainsets / 1509 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Hofuf rail network on OpenStreetMap](hofuf-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 19 / 98 / 24 |
| Route length | 143.1 km double track |
| Direct transfers / reachable line pairs | 14.6% / 100.0% |
| Residents within 800 m radial station catchments | 496,209 (2020 raster; 52.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 503 × 3-car `light-metro-3car` trainsets (445 peak revenue) |
| Peak network throughput | 273,600 passengers/hour |
| Practical service capacity | 2,544,480 passenger-trips/day |
| Annual paid-trip planning range | 464.4–743.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.5 km | 14 | 76 | NW Outer ↔ S Outer |
| line-2 | 24.8 km | 14 | 78 | SW Outer ↔ E Outer |
| line-3 | 24.0 km | 13 | 73 | N Outer ↔ S Outer |
| line-4 |  4.8 km | 4 | 18 | SW Inner ↔ SW Mid |
| line-5 |  4.8 km | 5 | 20 | NW Inner ↔ N Mid |
| line-6 |  2.6 km | 2 | 11 | NW Inner ↔ NE Inner |
| line-7 |  3.2 km | 3 | 14 | SE Inner ↔ SE Mid |
| line-8 |  9.5 km | 6 | 32 | N Mid ↔ NW Inner |
| line-9 |  2.0 km | 2 | 10 | NW Outer ↔ NW Outer |
| line-10 |  6.5 km | 5 | 24 | E Mid ↔ E Outer |
| line-11 |  2.2 km | 2 | 10 | E Mid ↔ NE Outer |
| line-12 |  5.0 km | 4 | 18 | S Mid ↔ SW Mid |
| line-13 |  8.7 km | 5 | 30 | N Mid ↔ NE Mid |
| line-14 |  2.3 km | 3 | 13 | NW Mid ↔ NW Mid |
| line-15 |  3.1 km | 2 | 12 | E Mid ↔ NE Mid |
| line-16 |  8.0 km | 7 | 29 | NW Inner ↔ N Outer |
| line-17 |  2.1 km | 2 | 10 | S Mid ↔ S Mid |
| line-18 |  4.0 km | 3 | 15 | E Mid ↔ NE Mid |
| line-19 |  2.1 km | 2 | 10 | SW Outer ↔ S Outer |
| **Total** | **143.1 km** | **98 unique** | **503** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 8,835 one-way journeys / 66,550 train-km/day |
| Annual traction demand | 314.8 GWh |
| Station/depot PV / storage | 117.5 MW / 797.5 MWh |
| Aggregate charging power | 47.0 MW |
| Dedicated solar plant | 30.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-13: 5.5 km / 44 kWh |
| Lowest traversal charging margin | line-13: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.10 bn |
| Stations | $552 M |
| Depots | $293 M |
| Rolling stock | $453 M |
| Dedicated solar plant | $24 M |
| Residual train control | $7.2 M |
| Charging microgrids | $9.8 M |
| EPC / project services | $169 M |
| **Total city programme** | **$2.60 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $550 M (21.1%) |
| Domestic / local capital | $2.05 bn (78.9%) |
| Annual public construction commitment | $181 M / yr for 5 years |
| Annual post-grace debt service | $126 M / yr |
| External capital saved vs default turnkey sensitivity | $4.14 bn |
| Capital + lifetime external interest saved | $9.22 bn |
| Annual OPEX | $170 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,104 assets / 6,294 tasks | [`hofuf-operations-manifest.json`](operations/hofuf-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hofuf.toml`](hofuf.toml) | Expanded simulator scenario |
| [`hofuf.corridor.geojson`](hofuf.corridor.geojson) | GIS corridor and stations |
| [`hofuf.design-quality.yaml`](hofuf.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hofuf
```
