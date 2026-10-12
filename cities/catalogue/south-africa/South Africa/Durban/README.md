# Durban — Urban Rail Network

**Country:** ZA · **Population:** 3,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Durban-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$14.27 bn (87.6%) of external capital** and **$17.54 bn of external interest**. Capital plus saved interest totals **$31.82 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **31.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **306.330 km to 364.937 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **201 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **812 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **812 metro-6car trainsets / 4872 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Durban rail network on OpenStreetMap](durban-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 201 / 49 |
| Route length | 458.3 km double track |
| Direct transfers / reachable line pairs | 38.5% / 100.0% |
| Residents within 800 m radial station catchments | 709,731 (2020 raster; 21.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 812 × 6-car `metro-6car` trainsets (733 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 62.1 km | 22 | 119 | NE Mid ↔ S Outer |
| line-2 | 47.6 km | 20 | 93 | SW Mid ↔ NE Mid |
| line-3 | 52.1 km | 28 | 116 | N Outer ↔ S Mid |
| line-4 | 27.4 km | 15 | 62 | SW Mid ↔ E Mid |
| line-5 | 35.9 km | 12 | 65 | E Mid ↔ NW Outer |
| line-6 | 32.9 km | 16 | 68 | W Mid ↔ SE Inner |
| line-7 | 34.1 km | 18 | 73 | NW Mid ↔ E Inner |
| line-8 | 30.2 km | 24 | 86 | W Mid ↔ E Inner |
| line-9 | 92.8 km | 29 | 42 | W Mid ↔ W Inner |
| line-10 | 10.3 km | 4 | 20 | S Mid ↔ SW Mid |
| line-11 |  6.3 km | 2 | 13 | N Mid ↔ N Mid |
| line-12 | 11.7 km | 4 | 21 | N Mid ↔ NW Inner |
| line-13 |  8.4 km | 4 | 19 | SW Mid ↔ S Outer |
| line-14 |  6.4 km | 3 | 15 | N Outer ↔ N Outer |
| **Total** | **458.3 km** | **201 unique** | **812** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 191,535 train-km/day |
| Annual traction demand | 1,812.1 GWh |
| Station/depot PV / storage | 123.1 MW / 914.0 MWh |
| Aggregate charging power | 382.0 MW |
| Dedicated solar plant | 1,047.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 15.4 km / 230 kWh |
| Lowest traversal charging margin | line-11: 92 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.48 bn |
| Stations | $1.35 bn |
| Depots | $372 M |
| Rolling stock | $1.36 bn |
| Dedicated solar plant | $838 M |
| Residual train control | $23 M |
| Charging microgrids | $77 M |
| EPC / project services | $537 M |
| **Total city programme** | **$9.05 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.01 bn (22.3%) |
| Domestic / local capital | $7.03 bn (77.7%) |
| Annual public construction commitment | $963 M / yr for 5 years |
| Annual post-grace debt service | $725 M / yr |
| External capital saved vs default turnkey sensitivity | $14.27 bn |
| Capital + lifetime external interest saved | $31.82 bn |
| Annual OPEX | $247 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,956 assets / 10,964 tasks | [`durban-operations-manifest.json`](operations/durban-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`durban.toml`](durban.toml) | Expanded simulator scenario |
| [`durban.corridor.geojson`](durban.corridor.geojson) | GIS corridor and stations |
| [`durban.design-quality.yaml`](durban.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh durban
```
