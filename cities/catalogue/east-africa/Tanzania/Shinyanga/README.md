# Shinyanga — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Shinyanga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.63 bn (89.5%) of external capital** and **$2.05 bn of external interest**. Capital plus saved interest totals **$3.68 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **6 additional residential lines**. **74.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **28.738 km to 45.378 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **42 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **147 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **147 tram-2car trainsets / 294 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Shinyanga rail network on OpenStreetMap](shinyanga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 42 / 8 |
| Route length | 56.2 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 85,721 (2020 raster; 58.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 147 × 2-car `tram-2car` trainsets (127 peak revenue) |
| Peak network throughput | 86,400 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.8 km | 11 | 35 | NE Outer ↔ SW Inner |
| line-2 |  7.8 km | 6 | 20 | NW Mid ↔ S Inner |
| line-3 |  6.7 km | 5 | 17 | SE Inner ↔ S Mid |
| line-4 |  2.5 km | 2 | 8 | NE Inner ↔ NW Inner |
| line-5 |  4.7 km | 3 | 12 | NE Inner ↔ SE Mid |
| line-6 |  3.1 km | 3 | 11 | W Inner ↔ W Mid |
| line-7 |  2.9 km | 2 | 9 | NE Inner ↔ N Mid |
| line-8 |  6.3 km | 4 | 15 | NE Inner ↔ E Mid |
| line-9 |  8.4 km | 6 | 20 | W Mid ↔ S Mid |
| **Total** | **56.2 km** | **42 unique** | **147** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,185 one-way journeys / 26,140 train-km/day |
| Annual traction demand | 82.4 GWh |
| Station/depot PV / storage | 52.8 MW / 373.0 MWh |
| Aggregate charging power | 17.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 8.0 km / 44 kWh |
| Lowest traversal charging margin | line-8: 27 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $540 M |
| Stations | $196 M |
| Depots | $122 M |
| Rolling stock | $82 M |
| Residual train control | $2.8 M |
| Charging microgrids | $3.6 M |
| EPC / project services | $66 M |
| **Total city programme** | **$1.01 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $192 M (19.0%) |
| Domestic / local capital | $821 M (81.0%) |
| Annual public construction commitment | $95 M / yr for 7 years |
| Annual post-grace debt service | $77 M / yr |
| External capital saved vs default turnkey sensitivity | $1.63 bn |
| Capital + lifetime external interest saved | $3.68 bn |
| Annual OPEX | $25 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 392 assets / 2,047 tasks | [`shinyanga-operations-manifest.json`](operations/shinyanga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`shinyanga.toml`](shinyanga.toml) | Expanded simulator scenario |
| [`shinyanga.corridor.geojson`](shinyanga.corridor.geojson) | GIS corridor and stations |
| [`shinyanga.design-quality.yaml`](shinyanga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh shinyanga
```
