# Hurghada — Urban Rail Network

**Country:** EG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hurghada-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$951 M (89.5%) of external capital** and **$1.17 bn of external interest**. Capital plus saved interest totals **$2.12 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **4 lines**, including **1 additional residential lines**. **74.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **33.000 km to 31.313 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **24 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **91 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **91 tram-2car trainsets / 182 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Hurghada rail network on OpenStreetMap](hurghada-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 24 / 4 |
| Route length | 37.2 km double track |
| Direct transfers / reachable line pairs | 50.0% / 100.0% |
| Residents within 800 m radial station catchments | 68,616 (2020 raster; 61.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 91 × 2-car `tram-2car` trainsets (80 peak revenue) |
| Peak network throughput | 38,400 passengers/hour |
| Practical service capacity | 357,120 passenger-trips/day |
| Annual paid-trip planning range | 65.2–104.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.2 km | 9 | 34 | NW Outer ↔ SE Mid |
| line-2 | 13.1 km | 7 | 28 | SE Outer ↔ NW Mid |
| line-3 |  5.3 km | 4 | 15 | E Mid ↔ S Mid |
| line-4 |  4.6 km | 4 | 14 | E Inner ↔ N Inner |
| **Total** | **37.2 km** | **24 unique** | **91** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,860 one-way journeys / 17,309 train-km/day |
| Annual traction demand | 54.6 GWh |
| Station/depot PV / storage | 26.0 MW / 170.0 MWh |
| Aggregate charging power | 12.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 2.9 km / 16 kWh |
| Lowest traversal charging margin | line-3: 50 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $320 M |
| Stations | $119 M |
| Depots | $57 M |
| Rolling stock | $51 M |
| Residual train control | $1.9 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $39 M |
| **Total city programme** | **$591 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $112 M (18.9%) |
| Domestic / local capital | $479 M (81.1%) |
| Annual public construction commitment | $64 M / yr for 5 years |
| Annual post-grace debt service | $48 M / yr |
| External capital saved vs default turnkey sensitivity | $951 M |
| Capital + lifetime external interest saved | $2.12 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 234 assets / 1,253 tasks | [`hurghada-operations-manifest.json`](operations/hurghada-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hurghada.toml`](hurghada.toml) | Expanded simulator scenario |
| [`hurghada.corridor.geojson`](hurghada.corridor.geojson) | GIS corridor and stations |
| [`hurghada.design-quality.yaml`](hurghada.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hurghada
```
