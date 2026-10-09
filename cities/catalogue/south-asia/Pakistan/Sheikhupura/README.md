# Sheikhupura — Urban Rail Network

**Country:** PK · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sheikhupura-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.41 bn (88.1%) of external capital** and **$1.77 bn of external interest**. Capital plus saved interest totals **$3.19 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **5 lines**, including **3 additional residential lines**. **34.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **16.553 km to 27.535 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **47 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **173 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **173 light-metro-3car trainsets / 519 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Sheikhupura rail network on OpenStreetMap](sheikhupura-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 47 / 6 |
| Route length | 29.5 km double track |
| Direct transfers / reachable line pairs | 60.0% / 100.0% |
| Residents within 800 m radial station catchments | 305,327 (2020 raster; 25.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 173 × 3-car `light-metro-3car` trainsets (155 peak revenue) |
| Peak network throughput | 72,000 passengers/hour |
| Practical service capacity | 669,600 passenger-trips/day |
| Annual paid-trip planning range | 122.2–195.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.1 km | 18 | 61 | W Mid ↔ E Mid |
| line-2 |  6.9 km | 18 | 60 | W Inner ↔ E Mid |
| line-3 |  5.2 km | 4 | 18 | E Inner ↔ S Mid |
| line-4 |  5.3 km | 4 | 19 | E Mid ↔ E Outer |
| line-5 |  4.0 km | 3 | 15 | E Inner ↔ N Mid |
| **Total** | **29.5 km** | **47 unique** | **173** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,325 one-way journeys / 13,739 train-km/day |
| Annual traction demand | 65.0 GWh |
| Station/depot PV / storage | 37.3 MW / 220.5 MWh |
| Aggregate charging power | 23.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 3.4 km / 28 kWh |
| Lowest traversal charging margin | line-4: 22 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $275 M |
| Stations | $312 M |
| Depots | $84 M |
| Rolling stock | $156 M |
| Residual train control | $1.5 M |
| Charging microgrids | $4.8 M |
| EPC / project services | $58 M |
| **Total city programme** | **$891 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $191 M (21.4%) |
| Domestic / local capital | $701 M (78.6%) |
| Annual public construction commitment | $121 M / yr for 7 years |
| Annual post-grace debt service | $104 M / yr |
| External capital saved vs default turnkey sensitivity | $1.41 bn |
| Capital + lifetime external interest saved | $3.19 bn |
| Annual OPEX | $24 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 444 assets / 2,410 tasks | [`sheikhupura-operations-manifest.json`](operations/sheikhupura-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sheikhupura.toml`](sheikhupura.toml) | Expanded simulator scenario |
| [`sheikhupura.corridor.geojson`](sheikhupura.corridor.geojson) | GIS corridor and stations |
| [`sheikhupura.design-quality.yaml`](sheikhupura.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sheikhupura
```
