# Taif — Urban Rail Network

**Country:** SA · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Taif-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.94 bn (88.2%) of external capital** and **$3.62 bn of external interest**. Capital plus saved interest totals **$6.57 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **61.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **50.031 km to 74.221 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **73 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **391 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **391 light-metro-3car trainsets / 1173 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Taif rail network on OpenStreetMap](taif-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 73 / 10 |
| Route length | 109.0 km double track |
| Direct transfers / reachable line pairs | 20.5% / 100.0% |
| Residents within 800 m radial station catchments | 202,472 (2020 raster; 45.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 391 × 3-car `light-metro-3car` trainsets (348 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.9 km | 16 | 83 | SE Outer ↔ NW Mid |
| line-2 | 12.4 km | 8 | 42 | S Mid ↔ NW Mid |
| line-3 | 18.9 km | 11 | 62 | NE Outer ↔ W Mid |
| line-4 |  5.0 km | 4 | 18 | NW Inner ↔ N Mid |
| line-5 |  9.7 km | 6 | 35 | S Inner ↔ SW Outer |
| line-6 |  5.6 km | 4 | 21 | W Inner ↔ W Mid |
| line-7 |  5.6 km | 4 | 19 | S Inner ↔ S Inner |
| line-8 |  2.9 km | 3 | 13 | W Inner ↔ N Inner |
| line-9 | 10.7 km | 6 | 39 | NW Mid ↔ N Mid |
| line-10 |  6.1 km | 4 | 24 | S Mid ↔ S Outer |
| line-11 |  2.4 km | 2 | 10 | N Inner ↔ N Inner |
| line-12 |  3.2 km | 3 | 14 | NE Inner ↔ NE Mid |
| line-13 |  2.7 km | 2 | 11 | NW Mid ↔ NW Mid |
| **Total** | **109.0 km** | **73 unique** | **391** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 50,686 train-km/day |
| Annual traction demand | 239.8 GWh |
| Station/depot PV / storage | 77.9 MW / 541.5 MWh |
| Aggregate charging power | 28.0 MW |
| Dedicated solar plant | 36.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 10.7 km / 86 kWh |
| Lowest traversal charging margin | line-6: 16 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $867 M |
| Stations | $271 M |
| Depots | $207 M |
| Rolling stock | $352 M |
| Dedicated solar plant | $29 M |
| Residual train control | $5.5 M |
| Charging microgrids | $5.8 M |
| EPC / project services | $119 M |
| **Total city programme** | **$1.86 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $395 M (21.3%) |
| Domestic / local capital | $1.46 bn (78.7%) |
| Annual public construction commitment | $129 M / yr for 5 years |
| Annual post-grace debt service | $90 M / yr |
| External capital saved vs default turnkey sensitivity | $2.94 bn |
| Capital + lifetime external interest saved | $6.57 bn |
| Annual OPEX | $125 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 825 assets / 4,785 tasks | [`taif-operations-manifest.json`](operations/taif-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`taif.toml`](taif.toml) | Expanded simulator scenario |
| [`taif.corridor.geojson`](taif.corridor.geojson) | GIS corridor and stations |
| [`taif.design-quality.yaml`](taif.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh taif
```
