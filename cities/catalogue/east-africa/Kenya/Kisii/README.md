# Kisii — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kisii-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.00 bn (89.2%) of external capital** and **$1.26 bn of external interest**. Capital plus saved interest totals **$2.26 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **41.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **21.211 km to 29.378 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **26 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **96 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **96 tram-2car trainsets / 192 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kisii rail network on OpenStreetMap](kisii-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 26 / 6 |
| Route length | 36.0 km double track |
| Direct transfers / reachable line pairs | 28.6% / 100.0% |
| Residents within 800 m radial station catchments | 107,167 (2020 raster; 30.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 96 × 2-car `tram-2car` trainsets (82 peak revenue) |
| Peak network throughput | 67,200 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  6.7 km | 4 | 16 | SE Outer ↔ W Mid |
| line-2 |  3.0 km | 3 | 11 | NW Inner ↔ SW Inner |
| line-3 |  8.5 km | 6 | 20 | N Outer ↔ SE Mid |
| line-4 |  2.8 km | 2 | 9 | SE Inner ↔ E Mid |
| line-5 |  5.5 km | 4 | 14 | W Mid ↔ W Outer |
| line-6 |  5.8 km | 4 | 15 | N Inner ↔ E Outer |
| line-7 |  3.7 km | 3 | 11 | E Inner ↔ S Mid |
| **Total** | **36.0 km** | **26 unique** | **96** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 16,744 train-km/day |
| Annual traction demand | 52.8 GWh |
| Station/depot PV / storage | 39.5 MW / 287.5 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 5.8 km / 29 kWh |
| Lowest traversal charging margin | line-6: 17 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $309 M |
| Stations | $124 M |
| Depots | $93 M |
| Rolling stock | $54 M |
| Residual train control | $1.8 M |
| Charging microgrids | $2.4 M |
| EPC / project services | $41 M |
| **Total city programme** | **$625 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $121 M (19.4%) |
| Domestic / local capital | $504 M (80.6%) |
| Annual public construction commitment | $66 M / yr for 7 years |
| Annual post-grace debt service | $55 M / yr |
| External capital saved vs default turnkey sensitivity | $1.00 bn |
| Capital + lifetime external interest saved | $2.26 bn |
| Annual OPEX | $17 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 252 assets / 1,310 tasks | [`kisii-operations-manifest.json`](operations/kisii-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kisii.toml`](kisii.toml) | Expanded simulator scenario |
| [`kisii.corridor.geojson`](kisii.corridor.geojson) | GIS corridor and stations |
| [`kisii.design-quality.yaml`](kisii.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kisii
```
