# Hama — Urban Rail Network

**Country:** SY · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hama-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.53 bn (88.5%) of external capital** and **$3.26 bn of external interest**. Capital plus saved interest totals **$5.79 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **69.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **44.726 km to 64.284 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **57 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **297 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **297 light-metro-3car trainsets / 891 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Hama rail network on OpenStreetMap](hama-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 57 / 12 |
| Route length | 83.3 km double track |
| Direct transfers / reachable line pairs | 27.3% / 100.0% |
| Residents within 800 m radial station catchments | 300,150 (2020 raster; 53.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 297 × 3-car `light-metro-3car` trainsets (263 peak revenue) |
| Peak network throughput | 158,400 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.8 km | 11 | 59 | NW Outer ↔ SE Mid |
| line-2 |  9.8 km | 9 | 38 | S Mid ↔ NE Mid |
| line-3 | 14.1 km | 9 | 47 | W Outer ↔ E Mid |
| line-4 |  3.7 km | 3 | 14 | E Inner ↔ NE Mid |
| line-5 |  7.4 km | 5 | 25 | NE Mid ↔ N Outer |
| line-6 |  5.2 km | 3 | 17 | SE Inner ↔ NW Inner |
| line-7 |  8.3 km | 5 | 31 | W Mid ↔ SW Outer |
| line-8 |  6.9 km | 4 | 25 | S Mid ↔ S Outer |
| line-9 |  3.1 km | 2 | 12 | SE Mid ↔ SE Mid |
| line-10 |  2.0 km | 2 | 10 | NE Mid ↔ N Mid |
| line-11 |  4.9 km | 4 | 19 | NW Inner ↔ N Outer |
| **Total** | **83.3 km** | **57 unique** | **297** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 38,714 train-km/day |
| Annual traction demand | 183.1 GWh |
| Station/depot PV / storage | 65.5 MW / 457.5 MWh |
| Aggregate charging power | 23.0 MW |
| Dedicated solar plant | 20.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 8.3 km / 67 kWh |
| Lowest traversal charging margin | line-8: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $759 M |
| Stations | $260 M |
| Depots | $171 M |
| Rolling stock | $267 M |
| Dedicated solar plant | $17 M |
| Residual train control | $4.2 M |
| Charging microgrids | $4.8 M |
| EPC / project services | $103 M |
| **Total city programme** | **$1.59 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $329 M (20.8%) |
| Domestic / local capital | $1.26 bn (79.2%) |
| Annual public construction commitment | $241 M / yr for 10 years |
| Annual post-grace debt service | $222 M / yr |
| External capital saved vs default turnkey sensitivity | $2.53 bn |
| Capital + lifetime external interest saved | $5.79 bn |
| Annual OPEX | $38 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 639 assets / 3,667 tasks | [`hama-operations-manifest.json`](operations/hama-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hama.toml`](hama.toml) | Expanded simulator scenario |
| [`hama.corridor.geojson`](hama.corridor.geojson) | GIS corridor and stations |
| [`hama.design-quality.yaml`](hama.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hama
```
