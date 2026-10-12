# Rajkot — Urban Rail Network

**Country:** IN · **Population:** 1,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rajkot-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.16 bn (89.2%) of external capital** and **$3.89 bn of external interest**. Capital plus saved interest totals **$7.06 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **5 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **122.630 km to 112.672 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **47 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **153 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **153 metro-4car trainsets / 612 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Rajkot rail network on OpenStreetMap](rajkot-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 47 / 8 |
| Route length | 121.1 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 153 × 4-car `metro-4car` trainsets (137 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.8 km | 9 | 39 | NE Outer ↔ S Mid |
| line-2 | 12.1 km | 6 | 25 | E Mid ↔ W Mid |
| line-3 | 12.7 km | 8 | 29 | SE Mid ↔ NW Inner |
| line-4 | 23.5 km | 9 | 39 | W Mid ↔ SE Outer |
| line-5 | 50.9 km | 15 | 21 | NW Outer ↔ W Outer |
| **Total** | **121.1 km** | **47 unique** | **153** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 44,472 train-km/day |
| Annual traction demand | 280.5 GWh |
| Station/depot PV / storage | 35.2 MW / 251.0 MWh |
| Aggregate charging power | 57.0 MW |
| Dedicated solar plant | 106.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 34.3 km / 369 kWh |
| Lowest traversal charging margin | line-5: 170 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.23 bn |
| Stations | $260 M |
| Depots | $87 M |
| Rolling stock | $171 M |
| Dedicated solar plant | $85 M |
| Residual train control | $6.1 M |
| Charging microgrids | $12 M |
| EPC / project services | $123 M |
| **Total city programme** | **$1.97 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $382 M (19.4%) |
| Domestic / local capital | $1.59 bn (80.6%) |
| Annual public construction commitment | $172 M / yr for 5 years |
| Annual post-grace debt service | $122 M / yr |
| External capital saved vs default turnkey sensitivity | $3.16 bn |
| Capital + lifetime external interest saved | $7.06 bn |
| Annual OPEX | $46 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 412 assets / 2,197 tasks | [`rajkot-operations-manifest.json`](operations/rajkot-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rajkot.toml`](rajkot.toml) | Expanded simulator scenario |
| [`rajkot.corridor.geojson`](rajkot.corridor.geojson) | GIS corridor and stations |
| [`rajkot.design-quality.yaml`](rajkot.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh rajkot
```
