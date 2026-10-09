# Arua — Urban Rail Network

**Country:** UG · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Arua-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.77 bn (89.1%) of external capital** and **$2.21 bn of external interest**. Capital plus saved interest totals **$3.98 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **69.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **31.915 km to 47.410 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **49 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **176 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **176 tram-2car trainsets / 352 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Arua rail network on OpenStreetMap](arua-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 49 / 9 |
| Route length | 64.5 km double track |
| Direct transfers / reachable line pairs | 21.2% / 100.0% |
| Residents within 800 m radial station catchments | 148,729 (2020 raster; 53.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 176 × 2-car `tram-2car` trainsets (150 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 1,071,360 passenger-trips/day |
| Annual paid-trip planning range | 195.5–312.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.8 km | 6 | 21 | NW Mid ↔ SE Mid |
| line-2 | 13.5 km | 9 | 32 | E Outer ↔ W Outer |
| line-3 | 10.5 km | 10 | 31 | NE Outer ↔ S Mid |
| line-4 |  2.7 km | 2 | 9 | NE Inner ↔ NW Inner |
| line-5 |  2.5 km | 2 | 8 | S Mid ↔ SW Mid |
| line-6 |  2.5 km | 2 | 8 | N Mid ↔ N Mid |
| line-7 |  3.7 km | 3 | 11 | NE Inner ↔ NE Mid |
| line-8 |  3.9 km | 3 | 11 | W Mid ↔ SW Mid |
| line-9 |  3.5 km | 3 | 10 | S Mid ↔ S Outer |
| line-10 |  5.9 km | 4 | 15 | NW Mid ↔ N Outer |
| line-11 |  4.2 km | 3 | 11 | N Mid ↔ NW Mid |
| line-12 |  2.9 km | 2 | 9 | E Outer ↔ E Mid |
| **Total** | **64.5 km** | **49 unique** | **176** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 29,992 train-km/day |
| Annual traction demand | 94.6 GWh |
| Station/depot PV / storage | 69.6 MW / 496.0 MWh |
| Aggregate charging power | 22.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-10: 5.9 km / 29 kWh |
| Lowest traversal charging margin | line-10: 17 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $524 M |
| Stations | $237 M |
| Depots | $161 M |
| Rolling stock | $99 M |
| Residual train control | $3.2 M |
| Charging microgrids | $4.6 M |
| EPC / project services | $72 M |
| **Total city programme** | **$1.10 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $215 M (19.5%) |
| Domestic / local capital | $886 M (80.5%) |
| Annual public construction commitment | $134 M / yr for 7 years |
| Annual post-grace debt service | $113 M / yr |
| External capital saved vs default turnkey sensitivity | $1.77 bn |
| Capital + lifetime external interest saved | $3.98 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 468 assets / 2,437 tasks | [`arua-operations-manifest.json`](operations/arua-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`arua.toml`](arua.toml) | Expanded simulator scenario |
| [`arua.corridor.geojson`](arua.corridor.geojson) | GIS corridor and stations |
| [`arua.design-quality.yaml`](arua.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh arua
```
