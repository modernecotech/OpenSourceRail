# Madurai — Urban Rail Network

**Country:** IN · **Population:** 1,600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Madurai-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.98 bn (88.7%) of external capital** and **$6.12 bn of external interest**. Capital plus saved interest totals **$11.10 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **176.984 km to 165.160 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **76 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **262 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **262 metro-4car trainsets / 1048 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Madurai rail network on OpenStreetMap](madurai-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 76 / 16 |
| Route length | 204.7 km double track |
| Direct transfers / reachable line pairs | 86.7% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 262 × 4-car `metro-4car` trainsets (235 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 36.5 km | 15 | 62 | NE Mid ↔ SW Outer |
| line-2 | 26.5 km | 11 | 43 | NE Outer ↔ W Inner |
| line-3 | 27.6 km | 10 | 45 | NW Mid ↔ SE Outer |
| line-4 | 22.9 km | 8 | 37 | S Inner ↔ NW Outer |
| line-5 | 23.8 km | 13 | 47 | W Outer ↔ E Inner |
| line-6 | 67.4 km | 19 | 28 | NW Mid ↔ W Mid |
| **Total** | **204.7 km** | **76 unique** | **262** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 79,512 train-km/day |
| Annual traction demand | 501.5 GWh |
| Station/depot PV / storage | 47.1 MW / 325.5 MWh |
| Aggregate charging power | 93.0 MW |
| Dedicated solar plant | 275.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 22.0 km / 220 kWh |
| Lowest traversal charging margin | line-2: 150 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.86 bn |
| Stations | $408 M |
| Depots | $121 M |
| Rolling stock | $293 M |
| Dedicated solar plant | $220 M |
| Residual train control | $10 M |
| Charging microgrids | $19 M |
| EPC / project services | $190 M |
| **Total city programme** | **$3.12 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $633 M (20.3%) |
| Domestic / local capital | $2.48 bn (79.7%) |
| Annual public construction commitment | $271 M / yr for 5 years |
| Annual post-grace debt service | $193 M / yr |
| External capital saved vs default turnkey sensitivity | $4.98 bn |
| Capital + lifetime external interest saved | $11.10 bn |
| Annual OPEX | $73 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 680 assets / 3,694 tasks | [`madurai-operations-manifest.json`](operations/madurai-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`madurai.toml`](madurai.toml) | Expanded simulator scenario |
| [`madurai.corridor.geojson`](madurai.corridor.geojson) | GIS corridor and stations |
| [`madurai.design-quality.yaml`](madurai.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh madurai
```
