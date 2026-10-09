# Tete — Urban Rail Network

**Country:** MZ · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tete-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.16 bn (89.0%) of external capital** and **$4.08 bn of external interest**. Capital plus saved interest totals **$7.23 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **64.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **37.923 km to 79.580 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **68 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **306 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **306 light-metro-3car trainsets / 918 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Tete rail network on OpenStreetMap](tete-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 68 / 13 |
| Route length | 80.2 km double track |
| Direct transfers / reachable line pairs | 27.3% / 100.0% |
| Residents within 800 m radial station catchments | 153,653 (2020 raster; 49.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 306 × 3-car `light-metro-3car` trainsets (271 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,607,040 passenger-trips/day |
| Annual paid-trip planning range | 293.3–469.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.1 km | 14 | 62 | NW Outer ↔ S Outer |
| line-2 | 11.7 km | 11 | 46 | SE Outer ↔ NW Mid |
| line-3 |  9.7 km | 10 | 40 | W Inner ↔ NE Outer |
| line-4 |  2.8 km | 3 | 13 | NE Mid ↔ NE Mid |
| line-5 |  3.2 km | 3 | 14 | SW Outer ↔ S Mid |
| line-6 |  3.5 km | 4 | 17 | SE Mid ↔ E Inner |
| line-7 |  2.2 km | 2 | 10 | N Inner ↔ NE Inner |
| line-8 |  7.8 km | 5 | 27 | W Inner ↔ S Outer |
| line-9 |  4.3 km | 3 | 15 | NE Mid ↔ N Outer |
| line-10 |  3.3 km | 3 | 14 | SW Mid ↔ W Outer |
| line-11 |  4.9 km | 4 | 19 | SE Mid ↔ E Mid |
| line-12 |  7.6 km | 6 | 29 | N Inner ↔ NE Outer |
| **Total** | **80.2 km** | **68 unique** | **306** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 37,274 train-km/day |
| Annual traction demand | 176.3 GWh |
| Station/depot PV / storage | 76.2 MW / 507.0 MWh |
| Aggregate charging power | 33.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-11: 4.5 km / 38 kWh |
| Lowest traversal charging margin | line-11: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $982 M |
| Stations | $391 M |
| Depots | $183 M |
| Rolling stock | $275 M |
| Residual train control | $4.0 M |
| Charging microgrids | $6.8 M |
| EPC / project services | $129 M |
| **Total city programme** | **$1.97 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $392 M (19.9%) |
| Domestic / local capital | $1.58 bn (80.1%) |
| Annual public construction commitment | $220 M / yr for 10 years |
| Annual post-grace debt service | $199 M / yr |
| External capital saved vs default turnkey sensitivity | $3.16 bn |
| Capital + lifetime external interest saved | $7.23 bn |
| Annual OPEX | $48 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 715 assets / 3,980 tasks | [`tete-operations-manifest.json`](operations/tete-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tete.toml`](tete.toml) | Expanded simulator scenario |
| [`tete.corridor.geojson`](tete.corridor.geojson) | GIS corridor and stations |
| [`tete.design-quality.yaml`](tete.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tete
```
