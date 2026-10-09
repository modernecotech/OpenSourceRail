# Asyut — Urban Rail Network

**Country:** EG · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Asyut-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.53 bn (88.3%) of external capital** and **$3.11 bn of external interest**. Capital plus saved interest totals **$5.63 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **71.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **39.893 km to 69.441 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **61 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **321 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **321 light-metro-3car trainsets / 963 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Asyut rail network on OpenStreetMap](asyut-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 61 / 10 |
| Route length | 89.9 km double track |
| Direct transfers / reachable line pairs | 26.7% / 100.0% |
| Residents within 800 m radial station catchments | 809,832 (2020 raster; 55.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 321 × 3-car `light-metro-3car` trainsets (287 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.0 km | 5 | 24 | SE Inner ↔ NW Inner |
| line-2 | 17.9 km | 12 | 62 | SW Inner ↔ NE Outer |
| line-3 | 21.1 km | 14 | 74 | SE Outer ↔ W Mid |
| line-4 |  5.2 km | 4 | 18 | NW Inner ↔ SW Inner |
| line-5 | 10.3 km | 7 | 39 | NE Inner ↔ NW Outer |
| line-6 |  3.1 km | 2 | 12 | NE Inner ↔ E Inner |
| line-7 |  4.0 km | 3 | 16 | W Mid ↔ W Outer |
| line-8 |  6.0 km | 4 | 21 | NW Inner ↔ N Mid |
| line-9 | 11.5 km | 7 | 40 | NE Inner ↔ SE Outer |
| line-10 |  3.9 km | 3 | 15 | NW Inner ↔ W Inner |
| **Total** | **89.9 km** | **61 unique** | **321** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 41,815 train-km/day |
| Annual traction demand | 197.8 GWh |
| Station/depot PV / storage | 60.8 MW / 436.0 MWh |
| Aggregate charging power | 46.0 MW |
| Dedicated solar plant | 33.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.0 km / 89 kWh |
| Lowest traversal charging margin | line-7: 62 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $763 M |
| Stations | $232 M |
| Depots | $163 M |
| Rolling stock | $289 M |
| Dedicated solar plant | $27 M |
| Residual train control | $4.5 M |
| Charging microgrids | $9.5 M |
| EPC / project services | $102 M |
| **Total city programme** | **$1.59 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $336 M (21.1%) |
| Domestic / local capital | $1.25 bn (78.9%) |
| Annual public construction commitment | $171 M / yr for 5 years |
| Annual post-grace debt service | $128 M / yr |
| External capital saved vs default turnkey sensitivity | $2.53 bn |
| Capital + lifetime external interest saved | $5.63 bn |
| Annual OPEX | $46 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 681 assets / 3,946 tasks | [`asyut-operations-manifest.json`](operations/asyut-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`asyut.toml`](asyut.toml) | Expanded simulator scenario |
| [`asyut.corridor.geojson`](asyut.corridor.geojson) | GIS corridor and stations |
| [`asyut.design-quality.yaml`](asyut.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh asyut
```
