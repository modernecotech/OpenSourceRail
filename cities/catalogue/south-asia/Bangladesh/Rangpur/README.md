# Rangpur — Urban Rail Network

**Country:** BD · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rangpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.30 bn (88.4%) of external capital** and **$2.88 bn of external interest**. Capital plus saved interest totals **$5.17 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **52.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **44.143 km to 65.426 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **51 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **261 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **261 light-metro-3car trainsets / 783 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Rangpur rail network on OpenStreetMap](rangpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 51 / 12 |
| Route length | 74.5 km double track |
| Direct transfers / reachable line pairs | 21.8% / 100.0% |
| Residents within 800 m radial station catchments | 464,752 (2020 raster; 39.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 261 × 3-car `light-metro-3car` trainsets (231 peak revenue) |
| Peak network throughput | 158,400 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.6 km | 8 | 37 | E Mid ↔ NW Mid |
| line-2 | 15.2 km | 9 | 49 | NE Outer ↔ S Mid |
| line-3 | 10.6 km | 8 | 39 | SW Mid ↔ NW Outer |
| line-4 |  2.4 km | 2 | 10 | NW Inner ↔ SW Inner |
| line-5 |  5.5 km | 4 | 19 | SE Inner ↔ SE Outer |
| line-6 |  5.0 km | 3 | 17 | SW Inner ↔ NW Mid |
| line-7 |  6.0 km | 4 | 21 | NW Mid ↔ NW Outer |
| line-8 |  5.8 km | 4 | 21 | S Mid ↔ S Outer |
| line-9 |  6.1 km | 4 | 23 | E Inner ↔ NE Mid |
| line-10 |  3.5 km | 3 | 14 | SW Mid ↔ SW Mid |
| line-11 |  2.7 km | 2 | 11 | NE Outer ↔ NE Outer |
| **Total** | **74.5 km** | **51 unique** | **261** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 34,663 train-km/day |
| Annual traction demand | 164.0 GWh |
| Station/depot PV / storage | 66.1 MW / 458.5 MWh |
| Aggregate charging power | 24.0 MW |
| Dedicated solar plant | 31.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 4.1 km / 30 kWh |
| Lowest traversal charging margin | line-7: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $674 M |
| Stations | $243 M |
| Depots | $165 M |
| Rolling stock | $235 M |
| Dedicated solar plant | $25 M |
| Residual train control | $3.7 M |
| Charging microgrids | $5.0 M |
| EPC / project services | $93 M |
| **Total city programme** | **$1.44 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $302 M (20.9%) |
| Domestic / local capital | $1.14 bn (79.1%) |
| Annual public construction commitment | $124 M / yr for 7 years |
| Annual post-grace debt service | $101 M / yr |
| External capital saved vs default turnkey sensitivity | $2.30 bn |
| Capital + lifetime external interest saved | $5.17 bn |
| Annual OPEX | $39 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 576 assets / 3,262 tasks | [`rangpur-operations-manifest.json`](operations/rangpur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rangpur.toml`](rangpur.toml) | Expanded simulator scenario |
| [`rangpur.corridor.geojson`](rangpur.corridor.geojson) | GIS corridor and stations |
| [`rangpur.design-quality.yaml`](rangpur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh rangpur
```
