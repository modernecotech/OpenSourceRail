# Malindi — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Malindi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.38 bn (89.4%) of external capital** and **$1.73 bn of external interest**. Capital plus saved interest totals **$3.11 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **8 lines**, including **5 additional residential lines**. **70.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **24.764 km to 41.327 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **32 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **123 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **123 tram-2car trainsets / 246 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Malindi rail network on OpenStreetMap](malindi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 32 / 7 |
| Route length | 47.6 km double track |
| Direct transfers / reachable line pairs | 35.7% / 100.0% |
| Residents within 800 m radial station catchments | 109,931 (2020 raster; 56.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 123 × 2-car `tram-2car` trainsets (106 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 714,240 passenger-trips/day |
| Annual paid-trip planning range | 130.3–208.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.7 km | 6 | 21 | NW Outer ↔ SE Mid |
| line-2 |  9.0 km | 6 | 23 | S Mid ↔ N Outer |
| line-3 |  6.7 km | 4 | 16 | N Outer ↔ SE Mid |
| line-4 |  3.4 km | 3 | 11 | SW Inner ↔ W Mid |
| line-5 |  5.0 km | 4 | 14 | S Mid ↔ S Outer |
| line-6 |  9.4 km | 5 | 20 | NE Mid ↔ SW Outer |
| line-7 |  2.7 km | 2 | 9 | N Mid ↔ NW Mid |
| line-8 |  2.6 km | 2 | 9 | NE Mid ↔ NE Outer |
| **Total** | **47.6 km** | **32 unique** | **123** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,720 one-way journeys / 22,123 train-km/day |
| Annual traction demand | 69.8 GWh |
| Station/depot PV / storage | 47.2 MW / 332.0 MWh |
| Aggregate charging power | 16.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.1 km / 15 kWh |
| Lowest traversal charging margin | line-7: 34 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $439 M |
| Stations | $180 M |
| Depots | $107 M |
| Rolling stock | $69 M |
| Residual train control | $2.4 M |
| Charging microgrids | $3.4 M |
| EPC / project services | $56 M |
| **Total city programme** | **$857 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $164 M (19.1%) |
| Domestic / local capital | $694 M (80.9%) |
| Annual public construction commitment | $91 M / yr for 7 years |
| Annual post-grace debt service | $75 M / yr |
| External capital saved vs default turnkey sensitivity | $1.38 bn |
| Capital + lifetime external interest saved | $3.11 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 319 assets / 1,678 tasks | [`malindi-operations-manifest.json`](operations/malindi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`malindi.toml`](malindi.toml) | Expanded simulator scenario |
| [`malindi.corridor.geojson`](malindi.corridor.geojson) | GIS corridor and stations |
| [`malindi.design-quality.yaml`](malindi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh malindi
```
