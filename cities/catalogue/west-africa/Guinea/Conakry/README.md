# Conakry — Urban Rail Network

**Country:** GN · **Population:** 2,010,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Conakry-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.09 bn (88.4%) of external capital** and **$5.29 bn of external interest**. Capital plus saved interest totals **$9.38 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **14 lines**, including **11 additional residential lines**. **80.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **60.568 km to 80.008 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **105 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **286 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **286 metro-4car trainsets / 1144 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Conakry rail network on OpenStreetMap](conakry-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 105 / 20 |
| Route length | 135.0 km double track |
| Direct transfers / reachable line pairs | 25.3% / 100.0% |
| Residents within 800 m radial station catchments | 695,268 (2020 raster; 65.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 286 × 4-car `metro-4car` trainsets (250 peak revenue) |
| Peak network throughput | 268,800 passengers/hour |
| Practical service capacity | 2,410,560 passenger-trips/day |
| Annual paid-trip planning range | 439.9–703.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.8 km | 24 | 75 | NE Outer ↔ SW Outer |
| line-2 | 18.0 km | 11 | 40 | SW Mid ↔ N Mid |
| line-3 | 37.4 km | 28 | 24 | NW Inner ↔ W Inner |
| line-4 |  6.5 km | 5 | 17 | NE Inner ↔ SE Inner |
| line-5 |  3.5 km | 4 | 12 | NE Mid ↔ NE Mid |
| line-6 |  3.3 km | 3 | 11 | NE Inner ↔ NE Mid |
| line-7 |  8.4 km | 6 | 19 | NE Mid ↔ NE Outer |
| line-8 |  2.8 km | 2 | 9 | N Inner ↔ E Inner |
| line-9 |  2.4 km | 2 | 9 | S Inner ↔ W Inner |
| line-10 |  6.7 km | 5 | 17 | NE Mid ↔ E Inner |
| line-11 |  3.6 km | 4 | 13 | N Mid ↔ NE Inner |
| line-12 |  6.7 km | 4 | 15 | NE Outer ↔ NE Outer |
| line-13 |  2.9 km | 2 | 9 | NE Mid ↔ NE Mid |
| line-14 |  5.9 km | 5 | 16 | N Mid ↔ NE Mid |
| **Total** | **135.0 km** | **105 unique** | **286** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 54,058 train-km/day |
| Annual traction demand | 341.0 GWh |
| Station/depot PV / storage | 93.7 MW / 678.5 MWh |
| Aggregate charging power | 139.5 MW |
| Dedicated solar plant | 116.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 8.4 km / 84 kWh |
| Lowest traversal charging margin | line-7: 55 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.18 bn |
| Stations | $565 M |
| Depots | $219 M |
| Rolling stock | $320 M |
| Dedicated solar plant | $93 M |
| Residual train control | $6.7 M |
| Charging microgrids | $29 M |
| EPC / project services | $162 M |
| **Total city programme** | **$2.57 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $537 M (20.9%) |
| Domestic / local capital | $2.03 bn (79.1%) |
| Annual public construction commitment | $228 M / yr for 10 years |
| Annual post-grace debt service | $206 M / yr |
| External capital saved vs default turnkey sensitivity | $4.09 bn |
| Capital + lifetime external interest saved | $9.38 bn |
| Annual OPEX | $61 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 869 assets / 4,415 tasks | [`conakry-operations-manifest.json`](operations/conakry-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`conakry.toml`](conakry.toml) | Expanded simulator scenario |
| [`conakry.corridor.geojson`](conakry.corridor.geojson) | GIS corridor and stations |
| [`conakry.design-quality.yaml`](conakry.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh conakry
```
