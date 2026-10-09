# Nyeri — Urban Rail Network

**Country:** KE · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nyeri-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.09 bn (89.5%) of external capital** and **$2.61 bn of external interest**. Capital plus saved interest totals **$4.70 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **66.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **31.390 km to 46.481 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **53 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **184 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **184 tram-2car trainsets / 368 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Nyeri rail network on OpenStreetMap](nyeri-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 53 / 11 |
| Route length | 65.5 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 92,932 (2020 raster; 54.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 184 × 2-car `tram-2car` trainsets (160 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 892,800 passenger-trips/day |
| Annual paid-trip planning range | 162.9–260.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.7 km | 8 | 26 | E Mid ↔ NW Mid |
| line-2 | 14.4 km | 10 | 35 | NE Outer ↔ SW Mid |
| line-3 | 10.0 km | 6 | 24 | W Outer ↔ N Mid |
| line-4 |  3.0 km | 4 | 12 | NW Inner ↔ S Inner |
| line-5 |  5.8 km | 6 | 19 | W Mid ↔ NE Inner |
| line-6 |  5.0 km | 4 | 14 | S Mid ↔ SE Mid |
| line-7 |  5.2 km | 4 | 14 | SW Mid ↔ W Mid |
| line-8 |  4.7 km | 4 | 13 | NE Outer ↔ NE Outer |
| line-9 |  2.0 km | 3 | 10 | S Inner ↔ SE Inner |
| line-10 |  6.9 km | 4 | 17 | E Mid ↔ SE Outer |
| **Total** | **65.5 km** | **53 unique** | **184** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 30,478 train-km/day |
| Annual traction demand | 96.1 GWh |
| Station/depot PV / storage | 60.5 MW / 417.5 MWh |
| Aggregate charging power | 22.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-10: 6.9 km / 34 kWh |
| Lowest traversal charging margin | line-10: 19 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $684 M |
| Stations | $278 M |
| Depots | $137 M |
| Rolling stock | $103 M |
| Residual train control | $3.3 M |
| Charging microgrids | $4.7 M |
| EPC / project services | $85 M |
| **Total city programme** | **$1.29 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $245 M (18.9%) |
| Domestic / local capital | $1.05 bn (81.1%) |
| Annual public construction commitment | $138 M / yr for 7 years |
| Annual post-grace debt service | $114 M / yr |
| External capital saved vs default turnkey sensitivity | $2.09 bn |
| Capital + lifetime external interest saved | $4.70 bn |
| Annual OPEX | $34 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 490 assets / 2,576 tasks | [`nyeri-operations-manifest.json`](operations/nyeri-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nyeri.toml`](nyeri.toml) | Expanded simulator scenario |
| [`nyeri.corridor.geojson`](nyeri.corridor.geojson) | GIS corridor and stations |
| [`nyeri.design-quality.yaml`](nyeri.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nyeri
```
