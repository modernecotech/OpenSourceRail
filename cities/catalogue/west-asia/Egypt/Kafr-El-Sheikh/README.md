# Kafr-El-Sheikh — Urban Rail Network

**Country:** EG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kafr-El-Sheikh-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.30 bn (89.3%) of external capital** and **$1.60 bn of external interest**. Capital plus saved interest totals **$2.91 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **8 lines**, including **5 additional residential lines**. **77.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **29.985 km to 39.089 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **36 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **132 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **132 tram-2car trainsets / 264 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kafr-El-Sheikh rail network on OpenStreetMap](kafr-el-sheikh-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 36 / 8 |
| Route length | 50.6 km double track |
| Direct transfers / reachable line pairs | 35.7% / 100.0% |
| Residents within 800 m radial station catchments | 313,166 (2020 raster; 61.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 132 × 2-car `tram-2car` trainsets (115 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 714,240 passenger-trips/day |
| Annual paid-trip planning range | 130.3–208.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.6 km | 8 | 30 | NE Outer ↔ SW Outer |
| line-2 |  8.2 km | 5 | 19 | NW Outer ↔ S Mid |
| line-3 |  4.5 km | 4 | 14 | NE Inner ↔ S Mid |
| line-4 |  3.0 km | 3 | 11 | SW Inner ↔ E Inner |
| line-5 |  5.7 km | 4 | 15 | S Mid ↔ SW Outer |
| line-6 |  7.4 km | 5 | 18 | S Inner ↔ SE Outer |
| line-7 |  5.2 km | 4 | 14 | NE Mid ↔ N Outer |
| line-8 |  3.1 km | 3 | 11 | NW Inner ↔ NW Mid |
| **Total** | **50.6 km** | **36 unique** | **132** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,720 one-way journeys / 23,537 train-km/day |
| Annual traction demand | 74.2 GWh |
| Station/depot PV / storage | 46.3 MW / 330.5 MWh |
| Aggregate charging power | 14.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 5.9 km / 32 kWh |
| Lowest traversal charging margin | line-5: 15 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $412 M |
| Stations | $159 M |
| Depots | $108 M |
| Rolling stock | $74 M |
| Residual train control | $2.5 M |
| Charging microgrids | $3.0 M |
| EPC / project services | $53 M |
| **Total city programme** | **$811 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $157 M (19.3%) |
| Domestic / local capital | $654 M (80.7%) |
| Annual public construction commitment | $88 M / yr for 5 years |
| Annual post-grace debt service | $66 M / yr |
| External capital saved vs default turnkey sensitivity | $1.30 bn |
| Capital + lifetime external interest saved | $2.91 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 342 assets / 1,804 tasks | [`kafr-el-sheikh-operations-manifest.json`](operations/kafr-el-sheikh-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kafr-el-sheikh.toml`](kafr-el-sheikh.toml) | Expanded simulator scenario |
| [`kafr-el-sheikh.corridor.geojson`](kafr-el-sheikh.corridor.geojson) | GIS corridor and stations |
| [`kafr-el-sheikh.design-quality.yaml`](kafr-el-sheikh.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kafr-el-sheikh
```
