# Beira — Urban Rail Network

**Country:** MZ · **Population:** 535,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beira-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.36 bn (88.3%) of external capital** and **$3.05 bn of external interest**. Capital plus saved interest totals **$5.42 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **74.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **33.540 km to 54.084 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **55 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **270 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **270 light-metro-3car trainsets / 810 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Beira rail network on OpenStreetMap](beira-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 55 / 14 |
| Route length | 75.8 km double track |
| Direct transfers / reachable line pairs | 17.9% / 100.0% |
| Residents within 800 m radial station catchments | 235,463 (2020 raster; 56.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 270 × 3-car `light-metro-3car` trainsets (237 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.9 km | 10 | 46 | S Outer ↔ N Mid |
| line-2 |  9.8 km | 7 | 32 | SW Mid ↔ E Mid |
| line-3 | 15.0 km | 9 | 49 | NW Outer ↔ E Mid |
| line-4 |  3.7 km | 3 | 14 | S Mid ↔ SW Mid |
| line-5 |  2.6 km | 2 | 11 | S Mid ↔ S Outer |
| line-6 |  3.4 km | 3 | 14 | W Inner ↔ E Inner |
| line-7 |  4.4 km | 3 | 16 | NE Inner ↔ N Mid |
| line-8 |  4.3 km | 3 | 15 | S Mid ↔ SE Mid |
| line-9 |  3.7 km | 3 | 15 | NW Mid ↔ N Mid |
| line-10 |  3.4 km | 3 | 14 | S Inner ↔ SW Inner |
| line-11 |  5.6 km | 4 | 19 | SE Mid ↔ E Outer |
| line-12 |  3.5 km | 3 | 14 | NW Outer ↔ NW Outer |
| line-13 |  2.5 km | 2 | 11 | E Inner ↔ NE Mid |
| **Total** | **75.8 km** | **55 unique** | **270** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 35,249 train-km/day |
| Annual traction demand | 166.7 GWh |
| Station/depot PV / storage | 76.7 MW / 539.5 MWh |
| Aggregate charging power | 26.0 MW |
| Dedicated solar plant | 21.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 4.4 km / 33 kWh |
| Lowest traversal charging margin | line-7: 13 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $635 M |
| Stations | $298 M |
| Depots | $189 M |
| Rolling stock | $243 M |
| Dedicated solar plant | $17 M |
| Residual train control | $3.8 M |
| Charging microgrids | $5.5 M |
| EPC / project services | $96 M |
| **Total city programme** | **$1.49 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $313 M (21.1%) |
| Domestic / local capital | $1.17 bn (78.9%) |
| Annual public construction commitment | $164 M / yr for 10 years |
| Annual post-grace debt service | $149 M / yr |
| External capital saved vs default turnkey sensitivity | $2.36 bn |
| Capital + lifetime external interest saved | $5.42 bn |
| Annual OPEX | $38 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 610 assets / 3,410 tasks | [`beira-operations-manifest.json`](operations/beira-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beira.toml`](beira.toml) | Expanded simulator scenario |
| [`beira.corridor.geojson`](beira.corridor.geojson) | GIS corridor and stations |
| [`beira.design-quality.yaml`](beira.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beira
```
