# Sanaa — Urban Rail Network

**Country:** YE · **Population:** 3,937,500 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sanaa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.99 bn (87.8%) of external capital** and **$11.61 bn of external interest**. Capital plus saved interest totals **$20.60 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **11 lines**, including **4 additional residential lines**. **53.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **192.451 km to 234.818 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **160 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **564 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **564 metro-6car trainsets / 3384 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Sanaa rail network on OpenStreetMap](sanaa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 160 / 32 |
| Route length | 289.3 km double track |
| Direct transfers / reachable line pairs | 43.6% / 100.0% |
| Residents within 800 m radial station catchments | 1,106,176 (2020 raster; 39.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 564 × 6-car `metro-6car` trainsets (505 peak revenue) |
| Peak network throughput | 316,800 passengers/hour |
| Practical service capacity | 2,812,320 passenger-trips/day |
| Annual paid-trip planning range | 513.2–821.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 44.6 km | 33 | 117 | NW Outer ↔ SE Mid |
| line-2 | 22.9 km | 19 | 69 | N Mid ↔ SE Mid |
| line-3 | 32.6 km | 8 | 60 | NW Mid ↔ SE Outer |
| line-4 | 22.1 km | 8 | 40 | S Mid ↔ NE Mid |
| line-5 | 34.6 km | 13 | 68 | E Outer ↔ W Mid |
| line-6 | 23.5 km | 14 | 56 | W Outer ↔ SE Inner |
| line-7 | 62.9 km | 34 | 36 | N Mid ↔ N Mid |
| line-8 |  5.1 km | 2 | 11 | S Inner ↔ S Inner |
| line-9 |  5.0 km | 3 | 14 | N Mid ↔ N Outer |
| line-10 | 15.0 km | 9 | 35 | S Mid ↔ S Outer |
| line-11 | 20.9 km | 17 | 58 | W Mid ↔ NW Inner |
| **Total** | **289.3 km** | **160 unique** | **564** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,882 one-way journeys / 119,878 train-km/day |
| Annual traction demand | 1,134.1 GWh |
| Station/depot PV / storage | 94.9 MW / 706.0 MWh |
| Aggregate charging power | 288.0 MW |
| Dedicated solar plant | 467.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-11: 16.1 km / 232 kWh |
| Lowest traversal charging margin | line-8: 115 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.63 bn |
| Stations | $1.05 bn |
| Depots | $273 M |
| Rolling stock | $948 M |
| Dedicated solar plant | $374 M |
| Residual train control | $14 M |
| Charging microgrids | $58 M |
| EPC / project services | $348 M |
| **Total city programme** | **$5.69 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.25 bn (22.0%) |
| Domestic / local capital | $4.44 bn (78.0%) |
| Annual public construction commitment | $784 M / yr for 10 years |
| Annual post-grace debt service | $720 M / yr |
| External capital saved vs default turnkey sensitivity | $8.99 bn |
| Capital + lifetime external interest saved | $20.60 bn |
| Annual OPEX | $130 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,454 assets / 7,942 tasks | [`sanaa-operations-manifest.json`](operations/sanaa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sanaa.toml`](sanaa.toml) | Expanded simulator scenario |
| [`sanaa.corridor.geojson`](sanaa.corridor.geojson) | GIS corridor and stations |
| [`sanaa.design-quality.yaml`](sanaa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sanaa
```
