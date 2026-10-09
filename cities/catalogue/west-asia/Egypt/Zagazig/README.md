# Zagazig — Urban Rail Network

**Country:** EG · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Zagazig-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.12 bn (88.4%) of external capital** and **$2.60 bn of external interest**. Capital plus saved interest totals **$4.72 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **6 additional residential lines**. **62.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **38.252 km to 59.472 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **49 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **255 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **255 light-metro-3car trainsets / 765 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Zagazig rail network on OpenStreetMap](zagazig-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 49 / 10 |
| Route length | 72.5 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 827,646 (2020 raster; 51.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 255 × 3-car `light-metro-3car` trainsets (228 peak revenue) |
| Peak network throughput | 129,600 passengers/hour |
| Practical service capacity | 1,205,280 passenger-trips/day |
| Annual paid-trip planning range | 220.0–351.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.8 km | 10 | 54 | NW Outer ↔ S Mid |
| line-2 |  8.6 km | 7 | 31 | SW Inner ↔ SE Mid |
| line-3 | 12.2 km | 8 | 41 | W Outer ↔ E Mid |
| line-4 |  3.7 km | 3 | 14 | SW Inner ↔ SE Inner |
| line-5 |  7.6 km | 5 | 27 | S Inner ↔ SW Mid |
| line-6 | 11.3 km | 7 | 41 | E Inner ↔ NE Outer |
| line-7 |  2.9 km | 2 | 11 | W Mid ↔ W Outer |
| line-8 |  4.4 km | 3 | 15 | W Inner ↔ SW Inner |
| line-9 |  6.1 km | 4 | 21 | E Mid ↔ SE Outer |
| **Total** | **72.5 km** | **49 unique** | **255** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,185 one-way journeys / 33,699 train-km/day |
| Annual traction demand | 159.4 GWh |
| Station/depot PV / storage | 54.9 MW / 376.5 MWh |
| Aggregate charging power | 21.0 MW |
| Dedicated solar plant | 20.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 8.9 km / 72 kWh |
| Lowest traversal charging margin | line-7: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $622 M |
| Stations | $227 M |
| Depots | $141 M |
| Rolling stock | $230 M |
| Dedicated solar plant | $16 M |
| Residual train control | $3.6 M |
| Charging microgrids | $4.4 M |
| EPC / project services | $86 M |
| **Total city programme** | **$1.33 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $278 M (20.9%) |
| Domestic / local capital | $1.05 bn (79.1%) |
| Annual public construction commitment | $143 M / yr for 5 years |
| Annual post-grace debt service | $107 M / yr |
| External capital saved vs default turnkey sensitivity | $2.12 bn |
| Capital + lifetime external interest saved | $4.72 bn |
| Annual OPEX | $38 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 551 assets / 3,161 tasks | [`zagazig-operations-manifest.json`](operations/zagazig-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`zagazig.toml`](zagazig.toml) | Expanded simulator scenario |
| [`zagazig.corridor.geojson`](zagazig.corridor.geojson) | GIS corridor and stations |
| [`zagazig.design-quality.yaml`](zagazig.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh zagazig
```
