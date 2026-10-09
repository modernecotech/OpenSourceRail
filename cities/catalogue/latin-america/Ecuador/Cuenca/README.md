# Cuenca — Urban Rail Network

**Country:** EC · **Population:** 817,100 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Cuenca-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.04 bn (88.2%) of external capital** and **$3.74 bn of external interest**. Capital plus saved interest totals **$6.78 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **78.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **53.360 km to 81.374 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **70 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **375 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **375 light-metro-3car trainsets / 1125 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Cuenca rail network on OpenStreetMap](cuenca-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 70 / 11 |
| Route length | 106.2 km double track |
| Direct transfers / reachable line pairs | 23.6% / 100.0% |
| Residents within 800 m radial station catchments | 347,375 (2020 raster; 61.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 375 × 3-car `light-metro-3car` trainsets (335 peak revenue) |
| Peak network throughput | 158,400 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.1 km | 12 | 69 | E Mid ↔ W Outer |
| line-2 | 19.6 km | 12 | 68 | NE Outer ↔ W Mid |
| line-3 | 19.2 km | 12 | 67 | NW Inner ↔ SE Outer |
| line-4 |  4.8 km | 3 | 17 | SW Mid ↔ SW Inner |
| line-5 |  5.4 km | 4 | 19 | SW Inner ↔ NE Inner |
| line-6 |  3.9 km | 3 | 14 | W Mid ↔ W Mid |
| line-7 |  5.3 km | 4 | 19 | W Inner ↔ W Mid |
| line-8 |  8.5 km | 6 | 30 | NW Inner ↔ NE Mid |
| line-9 |  2.9 km | 3 | 13 | E Inner ↔ SE Inner |
| line-10 |  7.1 km | 5 | 27 | E Mid ↔ NE Outer |
| line-11 |  8.7 km | 6 | 32 | W Mid ↔ SW Outer |
| **Total** | **106.2 km** | **70 unique** | **375** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 49,391 train-km/day |
| Annual traction demand | 233.6 GWh |
| Station/depot PV / storage | 66.7 MW / 459.5 MWh |
| Aggregate charging power | 25.0 MW |
| Dedicated solar plant | 76.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.7 km / 80 kWh |
| Lowest traversal charging margin | line-10: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $945 M |
| Stations | $258 M |
| Depots | $182 M |
| Rolling stock | $338 M |
| Dedicated solar plant | $61 M |
| Residual train control | $5.3 M |
| Charging microgrids | $5.2 M |
| EPC / project services | $121 M |
| **Total city programme** | **$1.92 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $408 M (21.3%) |
| Domestic / local capital | $1.51 bn (78.7%) |
| Annual public construction commitment | $193 M / yr for 5 years |
| Annual post-grace debt service | $143 M / yr |
| External capital saved vs default turnkey sensitivity | $3.04 bn |
| Capital + lifetime external interest saved | $6.78 bn |
| Annual OPEX | $61 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 785 assets / 4,579 tasks | [`cuenca-operations-manifest.json`](operations/cuenca-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`cuenca.toml`](cuenca.toml) | Expanded simulator scenario |
| [`cuenca.corridor.geojson`](cuenca.corridor.geojson) | GIS corridor and stations |
| [`cuenca.design-quality.yaml`](cuenca.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh cuenca
```
