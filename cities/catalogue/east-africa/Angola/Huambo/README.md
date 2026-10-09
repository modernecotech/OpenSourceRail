# Huambo — Urban Rail Network

**Country:** AO · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Huambo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.67 bn (88.6%) of external capital** and **$3.28 bn of external interest**. Capital plus saved interest totals **$5.96 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **51.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **47.453 km to 72.741 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **61 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **308 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **308 light-metro-3car trainsets / 924 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Huambo rail network on OpenStreetMap](huambo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 61 / 14 |
| Route length | 85.5 km double track |
| Direct transfers / reachable line pairs | 19.2% / 100.0% |
| Residents within 800 m radial station catchments | 133,295 (2020 raster; 36.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 308 × 3-car `light-metro-3car` trainsets (272 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.3 km | 13 | 65 | W Mid ↔ E Outer |
| line-2 | 10.0 km | 7 | 32 | E Mid ↔ SW Mid |
| line-3 | 13.6 km | 10 | 49 | N Mid ↔ SE Outer |
| line-4 |  4.6 km | 3 | 17 | NE Inner ↔ W Inner |
| line-5 |  2.7 km | 2 | 11 | W Mid ↔ NW Mid |
| line-6 |  7.4 km | 5 | 27 | SW Inner ↔ SE Mid |
| line-7 |  2.2 km | 2 | 10 | NE Mid ↔ NE Outer |
| line-8 |  8.9 km | 6 | 30 | NW Inner ↔ W Mid |
| line-9 |  5.8 km | 4 | 21 | W Mid ↔ W Outer |
| line-10 |  2.5 km | 2 | 10 | SE Mid ↔ SE Mid |
| line-11 |  2.5 km | 2 | 11 | NE Outer ↔ NE Outer |
| line-12 |  3.9 km | 3 | 15 | SW Mid ↔ W Mid |
| line-13 |  2.2 km | 2 | 10 | SE Outer ↔ S Outer |
| **Total** | **85.5 km** | **61 unique** | **308** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 39,774 train-km/day |
| Annual traction demand | 188.1 GWh |
| Station/depot PV / storage | 77.9 MW / 541.5 MWh |
| Aggregate charging power | 28.0 MW |
| Dedicated solar plant | 1.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 5.8 km / 48 kWh |
| Lowest traversal charging margin | line-9: 12 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $785 M |
| Stations | $297 M |
| Depots | $195 M |
| Rolling stock | $277 M |
| Dedicated solar plant | $1.3 M |
| Residual train control | $4.3 M |
| Charging microgrids | $5.8 M |
| EPC / project services | $110 M |
| **Total city programme** | **$1.68 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $344 M (20.6%) |
| Domestic / local capital | $1.33 bn (79.4%) |
| Annual public construction commitment | $191 M / yr for 5 years |
| Annual post-grace debt service | $145 M / yr |
| External capital saved vs default turnkey sensitivity | $2.67 bn |
| Capital + lifetime external interest saved | $5.96 bn |
| Annual OPEX | $47 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 682 assets / 3,858 tasks | [`huambo-operations-manifest.json`](operations/huambo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`huambo.toml`](huambo.toml) | Expanded simulator scenario |
| [`huambo.corridor.geojson`](huambo.corridor.geojson) | GIS corridor and stations |
| [`huambo.design-quality.yaml`](huambo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh huambo
```
