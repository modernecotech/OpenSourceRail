# Yaounde — Urban Rail Network

**Country:** CM · **Population:** 4,100,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Yaounde-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$10.09 bn (87.3%) of external capital** and **$12.65 bn of external interest**. Capital plus saved interest totals **$22.74 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **21 lines**, including **16 additional residential lines**. **82.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **179.501 km to 239.956 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **216 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**21 line-local depots** provide **691 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **691 metro-6car trainsets / 4146 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Yaounde rail network on OpenStreetMap](yaounde-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 21 / 216 / 45 |
| Route length | 316.0 km double track |
| Direct transfers / reachable line pairs | 25.2% / 100.0% |
| Residents within 800 m radial station catchments | 2,858,666 (2020 raster; 64.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 691 × 6-car `metro-6car` trainsets (617 peak revenue) |
| Peak network throughput | 604,800 passengers/hour |
| Practical service capacity | 5,490,720 passenger-trips/day |
| Annual paid-trip planning range | 1002.1–1603.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.7 km | 23 | 86 | NE Outer ↔ SW Mid |
| line-2 | 43.6 km | 25 | 97 | SE Mid ↔ NW Outer |
| line-3 | 30.1 km | 19 | 70 | E Outer ↔ NW Mid |
| line-4 | 16.6 km | 12 | 46 | E Mid ↔ W Inner |
| line-5 | 63.0 km | 44 | 41 | N Mid ↔ N Mid |
| line-6 |  5.2 km | 3 | 14 | SE Inner ↔ SE Inner |
| line-7 |  7.9 km | 7 | 26 | S Inner ↔ SW Inner |
| line-8 |  4.3 km | 3 | 13 | S Inner ↔ SW Inner |
| line-9 |  7.1 km | 5 | 20 | NE Inner ↔ SE Inner |
| line-10 |  6.5 km | 6 | 20 | SE Inner ↔ S Mid |
| line-11 |  7.2 km | 5 | 19 | S Inner ↔ SW Inner |
| line-12 |  4.1 km | 4 | 15 | SW Inner ↔ W Inner |
| line-13 |  4.1 km | 3 | 13 | SW Inner ↔ S Inner |
| line-14 | 12.0 km | 10 | 37 | S Inner ↔ W Inner |
| line-15 |  9.7 km | 7 | 27 | S Inner ↔ S Mid |
| line-16 | 15.9 km | 11 | 39 | S Inner ↔ SW Inner |
| line-17 |  4.3 km | 3 | 13 | E Mid ↔ E Inner |
| line-18 |  6.6 km | 4 | 17 | E Inner ↔ SE Inner |
| line-19 |  7.7 km | 7 | 25 | SE Inner ↔ S Inner |
| line-20 |  6.1 km | 4 | 16 | SW Inner ↔ W Inner |
| line-21 | 15.6 km | 11 | 37 | SE Inner ↔ S Mid |
| **Total** | **316.0 km** | **216 unique** | **691** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 9,532 one-way journeys / 132,284 train-km/day |
| Annual traction demand | 1,251.5 GWh |
| Station/depot PV / storage | 152.4 MW / 1,156.0 MWh |
| Aggregate charging power | 356.0 MW |
| Dedicated solar plant | 646.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 18.1 km / 271 kWh |
| Lowest traversal charging margin | line-20: 161 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.76 bn |
| Stations | $1.09 bn |
| Depots | $425 M |
| Rolling stock | $1.16 bn |
| Dedicated solar plant | $517 M |
| Residual train control | $16 M |
| Charging microgrids | $73 M |
| EPC / project services | $386 M |
| **Total city programme** | **$6.42 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.47 bn (22.9%) |
| Domestic / local capital | $4.95 bn (77.1%) |
| Annual public construction commitment | $545 M / yr for 7 years |
| Annual post-grace debt service | $448 M / yr |
| External capital saved vs default turnkey sensitivity | $10.09 bn |
| Capital + lifetime external interest saved | $22.74 bn |
| Annual OPEX | $161 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 43 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,879 assets / 9,998 tasks | [`yaounde-operations-manifest.json`](operations/yaounde-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`yaounde.toml`](yaounde.toml) | Expanded simulator scenario |
| [`yaounde.corridor.geojson`](yaounde.corridor.geojson) | GIS corridor and stations |
| [`yaounde.design-quality.yaml`](yaounde.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh yaounde
```
