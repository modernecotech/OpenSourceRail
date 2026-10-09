# Damanhur — Urban Rail Network

**Country:** EG · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damanhur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.44 bn (88.3%) of external capital** and **$3.00 bn of external interest**. Capital plus saved interest totals **$5.44 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **65.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **39.846 km to 63.858 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **58 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **304 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **304 light-metro-3car trainsets / 912 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Damanhur rail network on OpenStreetMap](damanhur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 58 / 15 |
| Route length | 82.2 km double track |
| Direct transfers / reachable line pairs | 30.9% / 100.0% |
| Residents within 800 m radial station catchments | 548,191 (2020 raster; 56.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 304 × 3-car `light-metro-3car` trainsets (271 peak revenue) |
| Peak network throughput | 158,400 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.4 km | 7 | 29 | N Mid ↔ S Inner |
| line-2 | 16.2 km | 10 | 56 | E Outer ↔ W Mid |
| line-3 | 18.3 km | 11 | 64 | W Mid ↔ NE Outer |
| line-4 |  2.9 km | 4 | 16 | SW Inner ↔ N Inner |
| line-5 |  6.7 km | 4 | 23 | N Inner ↔ NW Mid |
| line-6 |  5.7 km | 4 | 21 | S Inner ↔ S Mid |
| line-7 |  4.7 km | 3 | 18 | E Mid ↔ SE Mid |
| line-8 |  9.6 km | 6 | 32 | N Inner ↔ SE Mid |
| line-9 |  5.5 km | 4 | 21 | W Mid ↔ SW Outer |
| line-10 |  2.4 km | 3 | 13 | W Inner ↔ W Inner |
| line-11 |  2.7 km | 2 | 11 | W Inner ↔ S Inner |
| **Total** | **82.2 km** | **58 unique** | **304** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 38,243 train-km/day |
| Annual traction demand | 180.9 GWh |
| Station/depot PV / storage | 66.4 MW / 459.0 MWh |
| Aggregate charging power | 24.5 MW |
| Dedicated solar plant | 18.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 5.5 km / 44 kWh |
| Lowest traversal charging margin | line-7: 15 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $680 M |
| Stations | $286 M |
| Depots | $171 M |
| Rolling stock | $274 M |
| Dedicated solar plant | $15 M |
| Residual train control | $4.1 M |
| Charging microgrids | $5.1 M |
| EPC / project services | $99 M |
| **Total city programme** | **$1.53 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $323 M (21.1%) |
| Domestic / local capital | $1.21 bn (78.9%) |
| Annual public construction commitment | $165 M / yr for 5 years |
| Annual post-grace debt service | $123 M / yr |
| External capital saved vs default turnkey sensitivity | $2.44 bn |
| Capital + lifetime external interest saved | $5.44 bn |
| Annual OPEX | $44 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 654 assets / 3,757 tasks | [`damanhur-operations-manifest.json`](operations/damanhur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damanhur.toml`](damanhur.toml) | Expanded simulator scenario |
| [`damanhur.corridor.geojson`](damanhur.corridor.geojson) | GIS corridor and stations |
| [`damanhur.design-quality.yaml`](damanhur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh damanhur
```
