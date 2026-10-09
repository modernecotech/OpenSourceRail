# Morogoro — Urban Rail Network

**Country:** TZ · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Morogoro-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.92 bn (88.6%) of external capital** and **$3.66 bn of external interest**. Capital plus saved interest totals **$6.58 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **71.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **49.470 km to 76.915 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **61 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **308 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **308 light-metro-3car trainsets / 924 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Morogoro rail network on OpenStreetMap](morogoro-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 61 / 16 |
| Route length | 85.9 km double track |
| Direct transfers / reachable line pairs | 31.8% / 100.0% |
| Residents within 800 m radial station catchments | 234,880 (2020 raster; 54.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 308 × 3-car `light-metro-3car` trainsets (273 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,607,040 passenger-trips/day |
| Annual paid-trip planning range | 293.3–469.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.3 km | 11 | 52 | E Outer ↔ NW Mid |
| line-2 | 15.1 km | 10 | 52 | SW Outer ↔ NE Mid |
| line-3 | 13.0 km | 8 | 43 | S Outer ↔ NW Mid |
| line-4 |  2.1 km | 2 | 10 | SW Inner ↔ S Inner |
| line-5 |  3.9 km | 4 | 17 | N Inner ↔ N Mid |
| line-6 |  4.2 km | 3 | 15 | E Inner ↔ E Mid |
| line-7 |  6.0 km | 5 | 23 | W Inner ↔ N Mid |
| line-8 |  7.2 km | 4 | 26 | NW Mid ↔ N Mid |
| line-9 |  3.3 km | 3 | 14 | NW Mid ↔ NW Inner |
| line-10 |  5.8 km | 4 | 19 | S Inner ↔ NE Mid |
| line-11 |  7.6 km | 5 | 27 | S Inner ↔ E Mid |
| line-12 |  2.3 km | 2 | 10 | S Mid ↔ S Mid |
| **Total** | **85.9 km** | **61 unique** | **308** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 39,924 train-km/day |
| Annual traction demand | 188.9 GWh |
| Station/depot PV / storage | 73.5 MW / 502.5 MWh |
| Aggregate charging power | 28.5 MW |
| Dedicated solar plant | 39.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 7.2 km / 54 kWh |
| Lowest traversal charging margin | line-8: 22 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $886 M |
| Stations | $325 M |
| Depots | $184 M |
| Rolling stock | $277 M |
| Dedicated solar plant | $32 M |
| Residual train control | $4.3 M |
| Charging microgrids | $5.8 M |
| EPC / project services | $118 M |
| **Total city programme** | **$1.83 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $377 M (20.6%) |
| Domestic / local capital | $1.45 bn (79.4%) |
| Annual public construction commitment | $169 M / yr for 7 years |
| Annual post-grace debt service | $139 M / yr |
| External capital saved vs default turnkey sensitivity | $2.92 bn |
| Capital + lifetime external interest saved | $6.58 bn |
| Annual OPEX | $47 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 681 assets / 3,865 tasks | [`morogoro-operations-manifest.json`](operations/morogoro-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`morogoro.toml`](morogoro.toml) | Expanded simulator scenario |
| [`morogoro.corridor.geojson`](morogoro.corridor.geojson) | GIS corridor and stations |
| [`morogoro.design-quality.yaml`](morogoro.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh morogoro
```
