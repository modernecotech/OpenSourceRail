# Taif — Urban Rail Network

**Country:** SA · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Taif-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.82 bn (88.4%) of external capital** and **$2.23 bn of external interest**. Capital plus saved interest totals **$4.05 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **5 lines**, including **2 additional residential lines**. **22.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **50.031 km to 54.789 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **26 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **220 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **220 light-metro-3car trainsets / 660 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Taif rail network on OpenStreetMap](taif-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 26 / 4 |
| Route length | 70.9 km double track |
| Direct transfers / reachable line pairs | 40.0% / 100.0% |
| Residents within 800 m radial station catchments | 68,207 (2020 raster; 15.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 220 × 3-car `light-metro-3car` trainsets (198 peak revenue) |
| Peak network throughput | 72,000 passengers/hour |
| Practical service capacity | 669,600 passenger-trips/day |
| Annual paid-trip planning range | 122.2–195.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.9 km | 7 | 73 | SE Outer ↔ NW Mid |
| line-2 | 14.5 km | 5 | 43 | S Mid ↔ NW Mid |
| line-3 | 20.0 km | 9 | 62 | NE Mid ↔ W Mid |
| line-4 |  7.6 km | 3 | 26 | NW Inner ↔ N Mid |
| line-5 |  4.9 km | 2 | 16 | W Mid ↔ W Mid |
| **Total** | **70.9 km** | **26 unique** | **220** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,325 one-way journeys / 32,990 train-km/day |
| Annual traction demand | 156.1 GWh |
| Station/depot PV / storage | 30.1 MW / 208.5 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 47.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.5 km / 85 kWh |
| Lowest traversal charging margin | line-5: 13 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $613 M |
| Stations | $124 M |
| Depots | $90 M |
| Rolling stock | $198 M |
| Dedicated solar plant | $38 M |
| Residual train control | $3.5 M |
| Charging microgrids | $2.4 M |
| EPC / project services | $72 M |
| **Total city programme** | **$1.14 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $239 M (21.0%) |
| Domestic / local capital | $903 M (79.0%) |
| Annual public construction commitment | $79 M / yr for 5 years |
| Annual post-grace debt service | $55 M / yr |
| External capital saved vs default turnkey sensitivity | $1.82 bn |
| Capital + lifetime external interest saved | $4.05 bn |
| Annual OPEX | $64 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 390 assets / 2,450 tasks | [`taif-operations-manifest.json`](operations/taif-operations-manifest.json) |

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
