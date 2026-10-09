# Idlib — Urban Rail Network

**Country:** SY · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Idlib-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.25 bn (89.2%) of external capital** and **$1.62 bn of external interest**. Capital plus saved interest totals **$2.87 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **81.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **24.422 km to 29.069 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **37 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **132 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **132 tram-2car trainsets / 264 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Idlib rail network on OpenStreetMap](idlib-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 37 / 7 |
| Route length | 53.7 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 147,633 (2020 raster; 71.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 132 × 2-car `tram-2car` trainsets (116 peak revenue) |
| Peak network throughput | 67,200 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.7 km | 9 | 29 | NE Outer ↔ W Mid |
| line-2 |  8.0 km | 6 | 20 | NW Mid ↔ S Mid |
| line-3 |  8.6 km | 6 | 20 | NE Mid ↔ NW Inner |
| line-4 |  2.6 km | 2 | 9 | NW Inner ↔ E Inner |
| line-5 |  6.9 km | 4 | 16 | NE Mid ↔ N Mid |
| line-6 |  9.8 km | 6 | 23 | W Inner ↔ SE Outer |
| line-7 |  6.1 km | 4 | 15 | SW Mid ↔ SW Outer |
| **Total** | **53.7 km** | **37 unique** | **132** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 24,981 train-km/day |
| Annual traction demand | 78.8 GWh |
| Station/depot PV / storage | 40.7 MW / 289.5 MWh |
| Aggregate charging power | 13.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 8.6 km / 41 kWh |
| Lowest traversal charging margin | line-7: 17 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $381 M |
| Stations | $171 M |
| Depots | $97 M |
| Rolling stock | $74 M |
| Residual train control | $2.7 M |
| Charging microgrids | $2.9 M |
| EPC / project services | $51 M |
| **Total city programme** | **$780 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $152 M (19.5%) |
| Domestic / local capital | $628 M (80.5%) |
| Annual public construction commitment | $120 M / yr for 10 years |
| Annual post-grace debt service | $110 M / yr |
| External capital saved vs default turnkey sensitivity | $1.25 bn |
| Capital + lifetime external interest saved | $2.87 bn |
| Annual OPEX | $18 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 341 assets / 1,809 tasks | [`idlib-operations-manifest.json`](operations/idlib-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`idlib.toml`](idlib.toml) | Expanded simulator scenario |
| [`idlib.corridor.geojson`](idlib.corridor.geojson) | GIS corridor and stations |
| [`idlib.design-quality.yaml`](idlib.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh idlib
```
