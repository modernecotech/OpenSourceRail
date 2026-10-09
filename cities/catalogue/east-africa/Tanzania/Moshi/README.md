# Moshi — Urban Rail Network

**Country:** TZ · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Moshi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.70 bn (89.5%) of external capital** and **$2.13 bn of external interest**. Capital plus saved interest totals **$3.83 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **6 additional residential lines**. **65.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **31.509 km to 45.079 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **40 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **148 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **148 tram-2car trainsets / 296 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Moshi rail network on OpenStreetMap](moshi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 40 / 10 |
| Route length | 55.1 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 178,025 (2020 raster; 51.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 148 × 2-car `tram-2car` trainsets (127 peak revenue) |
| Peak network throughput | 86,400 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.2 km | 8 | 29 | NE Outer ↔ W Mid |
| line-2 |  9.1 km | 6 | 23 | NW Outer ↔ S Mid |
| line-3 |  6.9 km | 7 | 23 | NW Mid ↔ E Mid |
| line-4 |  2.5 km | 2 | 8 | SW Mid ↔ SE Inner |
| line-5 |  3.3 km | 3 | 10 | S Mid ↔ S Outer |
| line-6 |  3.7 km | 3 | 11 | NE Mid ↔ SE Mid |
| line-7 |  6.2 km | 4 | 15 | NW Inner ↔ SW Outer |
| line-8 |  2.8 km | 2 | 9 | N Mid ↔ N Outer |
| line-9 |  8.4 km | 5 | 20 | S Mid ↔ E Outer |
| **Total** | **55.1 km** | **40 unique** | **148** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,185 one-way journeys / 25,609 train-km/day |
| Annual traction demand | 80.8 GWh |
| Station/depot PV / storage | 53.1 MW / 373.5 MWh |
| Aggregate charging power | 18.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 8.4 km / 42 kWh |
| Lowest traversal charging margin | line-9: 19 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $558 M |
| Stations | $216 M |
| Depots | $123 M |
| Rolling stock | $83 M |
| Residual train control | $2.8 M |
| Charging microgrids | $3.8 M |
| EPC / project services | $69 M |
| **Total city programme** | **$1.06 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $200 M (18.9%) |
| Domestic / local capital | $856 M (81.1%) |
| Annual public construction commitment | $98 M / yr for 7 years |
| Annual post-grace debt service | $80 M / yr |
| External capital saved vs default turnkey sensitivity | $1.70 bn |
| Capital + lifetime external interest saved | $3.83 bn |
| Annual OPEX | $26 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 386 assets / 2,032 tasks | [`moshi-operations-manifest.json`](operations/moshi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`moshi.toml`](moshi.toml) | Expanded simulator scenario |
| [`moshi.corridor.geojson`](moshi.corridor.geojson) | GIS corridor and stations |
| [`moshi.design-quality.yaml`](moshi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh moshi
```
