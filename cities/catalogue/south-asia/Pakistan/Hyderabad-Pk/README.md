# Hyderabad-Pk — Urban Rail Network

**Country:** PK · **Population:** 1,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hyderabad-Pk-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.93 bn (88.8%) of external capital** and **$7.43 bn of external interest**. Capital plus saved interest totals **$13.35 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **15 lines**, including **9 additional residential lines**. **82.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **157.380 km to 179.190 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **136 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**15 line-local depots** provide **378 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **378 metro-4car trainsets / 1512 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Hyderabad-Pk rail network on OpenStreetMap](hyderabad-pk-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 15 / 136 / 29 |
| Route length | 202.3 km double track |
| Direct transfers / reachable line pairs | 29.5% / 100.0% |
| Residents within 800 m radial station catchments | 1,872,436 (2020 raster; 68.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 378 × 4-car `metro-4car` trainsets (333 peak revenue) |
| Peak network throughput | 288,000 passengers/hour |
| Practical service capacity | 2,589,120 passenger-trips/day |
| Annual paid-trip planning range | 472.5–756.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 11 | 37 | NE Mid ↔ SW Mid |
| line-2 | 16.2 km | 11 | 38 | W Mid ↔ SE Inner |
| line-3 | 15.6 km | 12 | 40 | S Mid ↔ N Mid |
| line-4 | 27.9 km | 18 | 59 | SE Mid ↔ N Outer |
| line-5 | 28.1 km | 17 | 56 | W Mid ↔ E Outer |
| line-6 | 55.0 km | 35 | 30 | W Mid ↔ W Mid |
| line-7 |  6.1 km | 5 | 17 | SE Mid ↔ S Inner |
| line-8 |  4.5 km | 3 | 12 | NE Inner ↔ NW Inner |
| line-9 |  3.6 km | 3 | 11 | SW Mid ↔ SW Outer |
| line-10 |  6.8 km | 5 | 16 | NW Mid ↔ NW Outer |
| line-11 |  5.1 km | 3 | 12 | S Mid ↔ S Outer |
| line-12 |  3.6 km | 3 | 11 | SE Inner ↔ SE Inner |
| line-13 |  5.7 km | 4 | 15 | NE Inner ↔ E Inner |
| line-14 |  4.7 km | 3 | 12 | SE Mid ↔ SE Mid |
| line-15 |  5.0 km | 3 | 12 | SW Inner ↔ S Inner |
| **Total** | **202.3 km** | **136 unique** | **378** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,742 one-way journeys / 81,299 train-km/day |
| Annual traction demand | 512.8 GWh |
| Station/depot PV / storage | 106.2 MW / 756.0 MWh |
| Aggregate charging power | 178.5 MW |
| Dedicated solar plant | 147.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 10.5 km / 113 kWh |
| Lowest traversal charging margin | line-11: 87 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.98 bn |
| Stations | $656 M |
| Depots | $249 M |
| Rolling stock | $423 M |
| Dedicated solar plant | $118 M |
| Residual train control | $10 M |
| Charging microgrids | $36 M |
| EPC / project services | $235 M |
| **Total city programme** | **$3.71 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $746 M (20.1%) |
| Domestic / local capital | $2.96 bn (79.9%) |
| Annual public construction commitment | $509 M / yr for 7 years |
| Annual post-grace debt service | $437 M / yr |
| External capital saved vs default turnkey sensitivity | $5.93 bn |
| Capital + lifetime external interest saved | $13.35 bn |
| Annual OPEX | $89 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 38 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,127 assets / 5,792 tasks | [`hyderabad-pk-operations-manifest.json`](operations/hyderabad-pk-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hyderabad-pk.toml`](hyderabad-pk.toml) | Expanded simulator scenario |
| [`hyderabad-pk.corridor.geojson`](hyderabad-pk.corridor.geojson) | GIS corridor and stations |
| [`hyderabad-pk.design-quality.yaml`](hyderabad-pk.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hyderabad-pk
```
