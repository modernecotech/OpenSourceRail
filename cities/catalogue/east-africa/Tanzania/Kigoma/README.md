# Kigoma — Urban Rail Network

**Country:** TZ · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kigoma-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.37 bn (89.3%) of external capital** and **$1.72 bn of external interest**. Capital plus saved interest totals **$3.09 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **79.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **32.263 km to 39.403 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **35 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **124 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **124 tram-2car trainsets / 248 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kigoma rail network on OpenStreetMap](kigoma-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 35 / 10 |
| Route length | 46.1 km double track |
| Direct transfers / reachable line pairs | 47.6% / 100.0% |
| Residents within 800 m radial station catchments | 179,898 (2020 raster; 64.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 124 × 2-car `tram-2car` trainsets (108 peak revenue) |
| Peak network throughput | 67,200 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.2 km | 6 | 23 | SW Outer ↔ E Mid |
| line-2 | 11.5 km | 8 | 29 | SE Outer ↔ NW Mid |
| line-3 |  6.1 km | 5 | 17 | N Mid ↔ S Mid |
| line-4 |  3.5 km | 3 | 11 | SE Mid ↔ S Mid |
| line-5 |  3.4 km | 3 | 11 | SW Mid ↔ W Inner |
| line-6 |  7.0 km | 5 | 18 | SE Inner ↔ N Mid |
| line-7 |  5.4 km | 5 | 15 | N Mid ↔ N Outer |
| **Total** | **46.1 km** | **35 unique** | **124** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 21,439 train-km/day |
| Annual traction demand | 67.6 GWh |
| Station/depot PV / storage | 42.8 MW / 293.0 MWh |
| Aggregate charging power | 16.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 4.6 km / 23 kWh |
| Lowest traversal charging margin | line-7: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $413 M |
| Stations | $212 M |
| Depots | $96 M |
| Rolling stock | $69 M |
| Residual train control | $2.3 M |
| Charging microgrids | $3.5 M |
| EPC / project services | $56 M |
| **Total city programme** | **$852 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $164 M (19.2%) |
| Domestic / local capital | $689 M (80.8%) |
| Annual public construction commitment | $79 M / yr for 7 years |
| Annual post-grace debt service | $65 M / yr |
| External capital saved vs default turnkey sensitivity | $1.37 bn |
| Capital + lifetime external interest saved | $3.09 bn |
| Annual OPEX | $21 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 331 assets / 1,736 tasks | [`kigoma-operations-manifest.json`](operations/kigoma-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kigoma.toml`](kigoma.toml) | Expanded simulator scenario |
| [`kigoma.corridor.geojson`](kigoma.corridor.geojson) | GIS corridor and stations |
| [`kigoma.design-quality.yaml`](kigoma.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kigoma
```
