# Bukavu — Urban Rail Network

**Country:** CD · **Population:** 1,000,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bukavu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.65 bn (88.3%) of external capital** and **$3.43 bn of external interest**. Capital plus saved interest totals **$6.08 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **6 additional residential lines**. **79.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **50.522 km to 73.040 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **62 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **307 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **307 light-metro-3car trainsets / 921 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bukavu rail network on OpenStreetMap](bukavu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 62 / 12 |
| Route length | 84.3 km double track |
| Direct transfers / reachable line pairs | 38.9% / 100.0% |
| Residents within 800 m radial station catchments | 658,586 (2020 raster; 61.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 307 × 3-car `light-metro-3car` trainsets (274 peak revenue) |
| Peak network throughput | 129,600 passengers/hour |
| Practical service capacity | 1,205,280 passenger-trips/day |
| Annual paid-trip planning range | 220.0–351.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.6 km | 9 | 48 | NE Outer ↔ SW Mid |
| line-2 | 22.0 km | 14 | 76 | NW Mid ↔ SE Outer |
| line-3 | 17.4 km | 11 | 57 | S Mid ↔ NE Outer |
| line-4 |  5.6 km | 6 | 25 | NW Inner ↔ NW Mid |
| line-5 |  3.3 km | 3 | 14 | SW Inner ↔ S Mid |
| line-6 |  3.0 km | 3 | 14 | SW Inner ↔ W Mid |
| line-7 |  5.9 km | 5 | 24 | NW Inner ↔ W Mid |
| line-8 |  5.6 km | 4 | 19 | SW Inner ↔ S Mid |
| line-9 |  7.8 km | 7 | 30 | SW Mid ↔ NW Mid |
| **Total** | **84.3 km** | **62 unique** | **307** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,185 one-way journeys / 39,215 train-km/day |
| Annual traction demand | 185.5 GWh |
| Station/depot PV / storage | 58.8 MW / 383.0 MWh |
| Aggregate charging power | 27.5 MW |
| Dedicated solar plant | 54.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.0 km / 75 kWh |
| Lowest traversal charging margin | line-8: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $774 M |
| Stations | $311 M |
| Depots | $149 M |
| Rolling stock | $276 M |
| Dedicated solar plant | $43 M |
| Residual train control | $4.2 M |
| Charging microgrids | $5.7 M |
| EPC / project services | $106 M |
| **Total city programme** | **$1.67 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $352 M (21.1%) |
| Domestic / local capital | $1.32 bn (78.9%) |
| Annual public construction commitment | $179 M / yr for 10 years |
| Annual post-grace debt service | $162 M / yr |
| External capital saved vs default turnkey sensitivity | $2.65 bn |
| Capital + lifetime external interest saved | $6.08 bn |
| Annual OPEX | $41 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 676 assets / 3,871 tasks | [`bukavu-operations-manifest.json`](operations/bukavu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bukavu.toml`](bukavu.toml) | Expanded simulator scenario |
| [`bukavu.corridor.geojson`](bukavu.corridor.geojson) | GIS corridor and stations |
| [`bukavu.design-quality.yaml`](bukavu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bukavu
```
