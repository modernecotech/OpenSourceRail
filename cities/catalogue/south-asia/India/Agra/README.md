# Agra — Urban Rail Network

**Country:** IN · **Population:** 1,700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Agra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.79 bn (89.2%) of external capital** and **$4.66 bn of external interest**. Capital plus saved interest totals **$8.44 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **5 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **147.193 km to 137.208 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **54 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **182 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **182 metro-4car trainsets / 728 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Agra rail network on OpenStreetMap](agra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 54 / 13 |
| Route length | 145.6 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 182 × 4-car `metro-4car` trainsets (162 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.6 km | 9 | 38 | NW Mid ↔ SE Outer |
| line-2 | 21.9 km | 9 | 38 | S Mid ↔ NE Outer |
| line-3 | 20.0 km | 8 | 35 | NE Outer ↔ W Mid |
| line-4 | 28.5 km | 11 | 48 | SE Outer ↔ NW Outer |
| line-5 | 54.6 km | 17 | 23 | W Mid ↔ W Mid |
| **Total** | **145.6 km** | **54 unique** | **182** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 54,996 train-km/day |
| Annual traction demand | 346.9 GWh |
| Station/depot PV / storage | 38.8 MW / 269.0 MWh |
| Aggregate charging power | 76.5 MW |
| Dedicated solar plant | 137.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.4 km / 80 kWh |
| Lowest traversal charging margin | line-2: 182 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.48 bn |
| Stations | $296 M |
| Depots | $94 M |
| Rolling stock | $204 M |
| Dedicated solar plant | $110 M |
| Residual train control | $7.3 M |
| Charging microgrids | $16 M |
| EPC / project services | $147 M |
| **Total city programme** | **$2.36 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $458 M (19.4%) |
| Domestic / local capital | $1.90 bn (80.6%) |
| Annual public construction commitment | $206 M / yr for 5 years |
| Annual post-grace debt service | $146 M / yr |
| External capital saved vs default turnkey sensitivity | $3.79 bn |
| Capital + lifetime external interest saved | $8.44 bn |
| Annual OPEX | $55 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 486 assets / 2,609 tasks | [`agra-operations-manifest.json`](operations/agra-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`agra.toml`](agra.toml) | Expanded simulator scenario |
| [`agra.corridor.geojson`](agra.corridor.geojson) | GIS corridor and stations |
| [`agra.design-quality.yaml`](agra.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh agra
```
