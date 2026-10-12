# Peshawar — Urban Rail Network

**Country:** PK · **Population:** 2,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Peshawar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.96 bn (89.1%) of external capital** and **$6.22 bn of external interest**. Capital plus saved interest totals **$11.18 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **8 lines**, including **3 additional residential lines**. **21.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **147.594 km to 161.613 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **61 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **257 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **257 metro-4car trainsets / 1028 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Peshawar rail network on OpenStreetMap](peshawar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 61 / 15 |
| Route length | 206.2 km double track |
| Direct transfers / reachable line pairs | 46.4% / 100.0% |
| Residents within 800 m radial station catchments | 546,767 (2020 raster; 14.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 257 × 4-car `metro-4car` trainsets (228 peak revenue) |
| Peak network throughput | 153,600 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.6 km | 9 | 50 | W Mid ↔ E Outer |
| line-2 | 29.0 km | 8 | 46 | SW Outer ↔ NE Mid |
| line-3 | 36.0 km | 11 | 59 | NW Outer ↔ SE Mid |
| line-4 | 25.5 km | 8 | 39 | NE Mid ↔ SW Mid |
| line-5 | 66.7 km | 18 | 27 | W Mid ↔ W Mid |
| line-6 |  5.6 km | 2 | 11 | SW Mid ↔ SW Outer |
| line-7 |  6.8 km | 2 | 13 | E Mid ↔ E Mid |
| line-8 |  5.1 km | 3 | 12 | S Inner ↔ SW Inner |
| **Total** | **206.2 km** | **61 unique** | **257** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 80,345 train-km/day |
| Annual traction demand | 506.8 GWh |
| Station/depot PV / storage | 53.5 MW / 387.5 MWh |
| Aggregate charging power | 79.5 MW |
| Dedicated solar plant | 204.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.0 km / 151 kWh |
| Lowest traversal charging margin | line-7: 67 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.96 bn |
| Stations | $318 M |
| Depots | $142 M |
| Rolling stock | $288 M |
| Dedicated solar plant | $164 M |
| Residual train control | $10 M |
| Charging microgrids | $16 M |
| EPC / project services | $192 M |
| **Total city programme** | **$3.09 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $609 M (19.7%) |
| Domestic / local capital | $2.49 bn (80.3%) |
| Annual public construction commitment | $426 M / yr for 7 years |
| Annual post-grace debt service | $366 M / yr |
| External capital saved vs default turnkey sensitivity | $4.96 bn |
| Capital + lifetime external interest saved | $11.18 bn |
| Annual OPEX | $70 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 608 assets / 3,392 tasks | [`peshawar-operations-manifest.json`](operations/peshawar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`peshawar.toml`](peshawar.toml) | Expanded simulator scenario |
| [`peshawar.corridor.geojson`](peshawar.corridor.geojson) | GIS corridor and stations |
| [`peshawar.design-quality.yaml`](peshawar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh peshawar
```
