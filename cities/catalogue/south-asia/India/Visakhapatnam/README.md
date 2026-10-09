# Visakhapatnam — Urban Rail Network

**Country:** IN · **Population:** 2,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Visakhapatnam-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.09 bn (88.6%) of external capital** and **$6.26 bn of external interest**. Capital plus saved interest totals **$11.34 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **171.319 km to 154.547 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **79 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **276 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **276 metro-4car trainsets / 1104 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Visakhapatnam rail network on OpenStreetMap](visakhapatnam-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 79 / 16 |
| Route length | 215.5 km double track |
| Direct transfers / reachable line pairs | 86.7% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 276 × 4-car `metro-4car` trainsets (248 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.3 km | 14 | 62 | E Outer ↔ SW Outer |
| line-2 | 39.7 km | 14 | 63 | SW Outer ↔ NE Outer |
| line-3 | 30.8 km | 14 | 53 | NW Outer ↔ SE Mid |
| line-4 | 23.1 km | 9 | 38 | W Outer ↔ NE Inner |
| line-5 | 19.3 km | 8 | 35 | N Mid ↔ S Inner |
| line-6 | 64.3 km | 20 | 25 | N Inner ↔ N Inner |
| **Total** | **215.5 km** | **79 unique** | **276** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 85,264 train-km/day |
| Annual traction demand | 537.8 GWh |
| Station/depot PV / storage | 49.8 MW / 339.0 MWh |
| Aggregate charging power | 108.0 MW |
| Dedicated solar plant | 295.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.0 km / 140 kWh |
| Lowest traversal charging margin | line-4: 138 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.89 bn |
| Stations | $409 M |
| Depots | $123 M |
| Rolling stock | $309 M |
| Dedicated solar plant | $237 M |
| Residual train control | $11 M |
| Charging microgrids | $22 M |
| EPC / project services | $193 M |
| **Total city programme** | **$3.19 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $653 M (20.5%) |
| Domestic / local capital | $2.54 bn (79.5%) |
| Annual public construction commitment | $277 M / yr for 5 years |
| Annual post-grace debt service | $198 M / yr |
| External capital saved vs default turnkey sensitivity | $5.09 bn |
| Capital + lifetime external interest saved | $11.34 bn |
| Annual OPEX | $75 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 25 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 717 assets / 3,900 tasks | [`visakhapatnam-operations-manifest.json`](operations/visakhapatnam-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`visakhapatnam.toml`](visakhapatnam.toml) | Expanded simulator scenario |
| [`visakhapatnam.corridor.geojson`](visakhapatnam.corridor.geojson) | GIS corridor and stations |
| [`visakhapatnam.design-quality.yaml`](visakhapatnam.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh visakhapatnam
```
