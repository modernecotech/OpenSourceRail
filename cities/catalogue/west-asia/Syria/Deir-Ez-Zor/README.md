# Deir-Ez-Zor — Urban Rail Network

**Country:** SY · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Deir-Ez-Zor-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.62 bn (88.6%) of external capital** and **$4.67 bn of external interest**. Capital plus saved interest totals **$8.29 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **81.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **41.984 km to 71.086 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **90 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **395 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **395 light-metro-3car trainsets / 1185 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Deir-Ez-Zor rail network on OpenStreetMap](deir-ez-zor-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 90 / 15 |
| Route length | 98.8 km double track |
| Direct transfers / reachable line pairs | 24.2% / 100.0% |
| Residents within 800 m radial station catchments | 276,427 (2020 raster; 66.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 395 × 3-car `light-metro-3car` trainsets (353 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,607,040 passenger-trips/day |
| Annual paid-trip planning range | 293.3–469.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.9 km | 23 | 86 | NW Mid ↔ SE Outer |
| line-2 | 12.8 km | 9 | 45 | NE Mid ↔ SW Mid |
| line-3 | 15.9 km | 12 | 56 | E Outer ↔ SW Inner |
| line-4 |  2.2 km | 2 | 10 | NE Inner ↔ E Inner |
| line-5 |  5.6 km | 5 | 21 | SW Inner ↔ SE Inner |
| line-6 |  4.8 km | 3 | 17 | NE Inner ↔ N Mid |
| line-7 |  3.7 km | 3 | 14 | E Inner ↔ E Mid |
| line-8 |  5.7 km | 4 | 21 | NW Mid ↔ NW Outer |
| line-9 | 10.5 km | 7 | 36 | W Inner ↔ NW Mid |
| line-10 |  8.3 km | 6 | 32 | E Mid ↔ SE Outer |
| line-11 |  3.3 km | 3 | 14 | SE Mid ↔ S Mid |
| line-12 |  4.9 km | 13 | 43 | W Mid ↔ NW Mid |
| **Total** | **98.8 km** | **90 unique** | **395** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 45,927 train-km/day |
| Annual traction demand | 217.3 GWh |
| Station/depot PV / storage | 79.2 MW / 512.0 MWh |
| Aggregate charging power | 38.0 MW |
| Dedicated solar plant | 23.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-10: 8.3 km / 67 kWh |
| Lowest traversal charging margin | line-8: 15 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.03 bn |
| Stations | $504 M |
| Depots | $195 M |
| Rolling stock | $356 M |
| Dedicated solar plant | $18 M |
| Residual train control | $4.9 M |
| Charging microgrids | $7.8 M |
| EPC / project services | $147 M |
| **Total city programme** | **$2.27 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $465 M (20.5%) |
| Domestic / local capital | $1.80 bn (79.5%) |
| Annual public construction commitment | $345 M / yr for 10 years |
| Annual post-grace debt service | $318 M / yr |
| External capital saved vs default turnkey sensitivity | $3.62 bn |
| Capital + lifetime external interest saved | $8.29 bn |
| Annual OPEX | $53 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 916 assets / 5,143 tasks | [`deir-ez-zor-operations-manifest.json`](operations/deir-ez-zor-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`deir-ez-zor.toml`](deir-ez-zor.toml) | Expanded simulator scenario |
| [`deir-ez-zor.corridor.geojson`](deir-ez-zor.corridor.geojson) | GIS corridor and stations |
| [`deir-ez-zor.design-quality.yaml`](deir-ez-zor.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh deir-ez-zor
```
