# Bandung — Urban Rail Network

**Country:** ID · **Population:** 2,615,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bandung-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.00 bn (88.5%) of external capital** and **$7.37 bn of external interest**. Capital plus saved interest totals **$13.37 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **159.882 km to 140.667 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **122 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **340 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **340 metro-4car trainsets / 1360 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bandung rail network on OpenStreetMap](bandung-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 122 / 19 |
| Route length | 218.4 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 340 × 4-car `metro-4car` trainsets (306 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.6 km | 15 | 61 | E Mid ↔ W Outer |
| line-2 | 39.0 km | 15 | 63 | SE Mid ↔ NW Outer |
| line-3 | 17.8 km | 25 | 71 | SW Inner ↔ NE Mid |
| line-4 | 29.7 km | 14 | 56 | S Mid ↔ N Outer |
| line-5 | 28.7 km | 14 | 54 | SE Mid ↔ N Outer |
| line-6 | 68.6 km | 39 | 35 | NW Mid ↔ W Mid |
| **Total** | **218.4 km** | **122 unique** | **340** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 85,587 train-km/day |
| Annual traction demand | 539.8 GWh |
| Station/depot PV / storage | 62.4 MW / 402.0 MWh |
| Aggregate charging power | 171.0 MW |
| Dedicated solar plant | 282.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 14.2 km / 142 kWh |
| Lowest traversal charging margin | line-2: 283 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.81 bn |
| Stations | $937 M |
| Depots | $135 M |
| Rolling stock | $381 M |
| Dedicated solar plant | $226 M |
| Residual train control | $11 M |
| Charging microgrids | $38 M |
| EPC / project services | $232 M |
| **Total city programme** | **$3.77 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $783 M (20.8%) |
| Domestic / local capital | $2.98 bn (79.2%) |
| Annual public construction commitment | $315 M / yr for 5 years |
| Annual post-grace debt service | $223 M / yr |
| External capital saved vs default turnkey sensitivity | $6.00 bn |
| Capital + lifetime external interest saved | $13.37 bn |
| Annual OPEX | $95 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 23 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,004 assets / 5,255 tasks | [`bandung-operations-manifest.json`](operations/bandung-operations-manifest.json) |

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
