# Dakar — Urban Rail Network

**Country:** SN · **Population:** 4,030,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dakar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.52 bn (87.6%) of external capital** and **$10.68 bn of external interest**. Capital plus saved interest totals **$19.20 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **14 lines**, including **8 additional residential lines**. **84.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **180.000 km to 218.136 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **188 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **583 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **583 metro-6car trainsets / 3498 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Dakar rail network on OpenStreetMap](dakar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 188 / 36 |
| Route length | 266.3 km double track |
| Direct transfers / reachable line pairs | 31.9% / 100.0% |
| Residents within 800 m radial station catchments | 2,520,085 (2020 raster; 68.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 583 × 6-car `metro-6car` trainsets (523 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.9 km | 19 | 73 | E Outer ↔ W Mid |
| line-2 | 28.6 km | 27 | 93 | W Mid ↔ E Mid |
| line-3 | 27.2 km | 17 | 65 | W Mid ↔ NE Outer |
| line-4 | 22.4 km | 16 | 61 | NE Mid ↔ SW Mid |
| line-5 | 35.9 km | 28 | 98 | E Outer ↔ SW Mid |
| line-6 | 61.8 km | 42 | 40 | W Mid ↔ W Mid |
| line-7 |  7.8 km | 6 | 23 | NE Inner ↔ NW Inner |
| line-8 |  4.5 km | 3 | 13 | E Inner ↔ E Mid |
| line-9 |  6.5 km | 4 | 16 | W Mid ↔ W Mid |
| line-10 |  4.6 km | 4 | 16 | W Mid ↔ W Mid |
| line-11 |  6.5 km | 5 | 19 | NE Mid ↔ E Inner |
| line-12 |  9.7 km | 6 | 23 | W Mid ↔ W Outer |
| line-13 |  8.5 km | 7 | 25 | W Mid ↔ SW Mid |
| line-14 |  7.4 km | 4 | 18 | NW Inner ↔ NE Mid |
| **Total** | **266.3 km** | **188 unique** | **583** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 109,455 train-km/day |
| Annual traction demand | 1,035.5 GWh |
| Station/depot PV / storage | 117.7 MW / 878.0 MWh |
| Aggregate charging power | 346.0 MW |
| Dedicated solar plant | 366.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.4 km / 174 kWh |
| Lowest traversal charging margin | line-9: 77 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.31 bn |
| Stations | $1.09 bn |
| Depots | $316 M |
| Rolling stock | $979 M |
| Dedicated solar plant | $293 M |
| Residual train control | $13 M |
| Charging microgrids | $70 M |
| EPC / project services | $334 M |
| **Total city programme** | **$5.40 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.20 bn (22.3%) |
| Domestic / local capital | $4.20 bn (77.7%) |
| Annual public construction commitment | $460 M / yr for 7 years |
| Annual post-grace debt service | $377 M / yr |
| External capital saved vs default turnkey sensitivity | $8.52 bn |
| Capital + lifetime external interest saved | $19.20 bn |
| Annual OPEX | $135 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 38 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,623 assets / 8,615 tasks | [`dakar-operations-manifest.json`](operations/dakar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`dakar.toml`](dakar.toml) | Expanded simulator scenario |
| [`dakar.corridor.geojson`](dakar.corridor.geojson) | GIS corridor and stations |
| [`dakar.design-quality.yaml`](dakar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh dakar
```
