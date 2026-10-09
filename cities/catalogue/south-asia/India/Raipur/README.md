# Raipur — Urban Rail Network

**Country:** IN · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Raipur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.45 bn (88.6%) of external capital** and **$4.24 bn of external interest**. Capital plus saved interest totals **$7.70 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **127.024 km to 115.077 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **51 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **202 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **202 metro-4car trainsets / 808 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Raipur rail network on OpenStreetMap](raipur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 51 / 11 |
| Route length | 139.8 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 202 × 4-car `metro-4car` trainsets (180 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.6 km | 12 | 49 | E Outer ↔ W Outer |
| line-2 | 26.2 km | 7 | 42 | S Mid ↔ N Outer |
| line-3 | 12.7 km | 6 | 25 | NE Mid ↔ W Mid |
| line-4 | 20.1 km | 10 | 38 | SE Outer ↔ W Mid |
| line-5 | 21.5 km | 8 | 35 | N Outer ↔ S Mid |
| line-6 | 29.6 km | 8 | 13 | E Inner ↔ E Inner |
| **Total** | **139.8 km** | **51 unique** | **202** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 58,113 train-km/day |
| Annual traction demand | 366.5 GWh |
| Station/depot PV / storage | 41.4 MW / 297.0 MWh |
| Aggregate charging power | 66.0 MW |
| Dedicated solar plant | 193.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.3 km / 102 kWh |
| Lowest traversal charging margin | line-2: 154 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.26 bn |
| Stations | $265 M |
| Depots | $108 M |
| Rolling stock | $226 M |
| Dedicated solar plant | $154 M |
| Residual train control | $7.0 M |
| Charging microgrids | $14 M |
| EPC / project services | $132 M |
| **Total city programme** | **$2.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $446 M (20.6%) |
| Domestic / local capital | $1.72 bn (79.4%) |
| Annual public construction commitment | $188 M / yr for 5 years |
| Annual post-grace debt service | $134 M / yr |
| External capital saved vs default turnkey sensitivity | $3.45 bn |
| Capital + lifetime external interest saved | $7.70 bn |
| Annual OPEX | $52 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 492 assets / 2,719 tasks | [`raipur-operations-manifest.json`](operations/raipur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`raipur.toml`](raipur.toml) | Expanded simulator scenario |
| [`raipur.corridor.geojson`](raipur.corridor.geojson) | GIS corridor and stations |
| [`raipur.design-quality.yaml`](raipur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh raipur
```
