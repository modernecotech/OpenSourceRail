# Bandung — Urban Rail Network

**Country:** ID · **Population:** 2,615,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bandung-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.25 bn (88.5%) of external capital** and **$10.14 bn of external interest**. Capital plus saved interest totals **$18.40 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **6 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **159.882 km to 177.914 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **189 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **507 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **507 metro-4car trainsets / 2028 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bandung rail network on OpenStreetMap](bandung-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 189 / 23 |
| Route length | 254.7 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 507 × 4-car `metro-4car` trainsets (458 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 41.6 km | 20 | 76 | E Mid ↔ W Outer |
| line-2 | 48.6 km | 36 | 117 | SE Mid ↔ NW Outer |
| line-3 | 24.6 km | 35 | 97 | SW Mid ↔ NE Mid |
| line-4 | 34.8 km | 33 | 102 | S Mid ↔ N Outer |
| line-5 | 32.3 km | 23 | 78 | SE Mid ↔ N Outer |
| line-6 | 72.8 km | 42 | 37 | W Mid ↔ W Mid |
| **Total** | **254.7 km** | **189 unique** | **507** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 101,523 train-km/day |
| Annual traction demand | 640.3 GWh |
| Station/depot PV / storage | 82.2 MW / 501.0 MWh |
| Aggregate charging power | 270.0 MW |
| Dedicated solar plant | 325.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 15.3 km / 153 kWh |
| Lowest traversal charging margin | line-1: 474 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.45 bn |
| Stations | $1.35 bn |
| Depots | $169 M |
| Rolling stock | $568 M |
| Dedicated solar plant | $261 M |
| Residual train control | $13 M |
| Charging microgrids | $55 M |
| EPC / project services | $322 M |
| **Total city programme** | **$5.18 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.07 bn (20.7%) |
| Domestic / local capital | $4.11 bn (79.3%) |
| Annual public construction commitment | $433 M / yr for 5 years |
| Annual post-grace debt service | $307 M / yr |
| External capital saved vs default turnkey sensitivity | $8.25 bn |
| Capital + lifetime external interest saved | $18.40 bn |
| Annual OPEX | $133 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,531 assets / 7,986 tasks | [`bandung-operations-manifest.json`](operations/bandung-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bandung.toml`](bandung.toml) | Expanded simulator scenario |
| [`bandung.corridor.geojson`](bandung.corridor.geojson) | GIS corridor and stations |
| [`bandung.design-quality.yaml`](bandung.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bandung
```
