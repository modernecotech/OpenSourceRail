# Bhopal — Urban Rail Network

**Country:** IN · **Population:** 2,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bhopal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.26 bn (89.0%) of external capital** and **$5.23 bn of external interest**. Capital plus saved interest totals **$9.49 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **172.859 km to 152.587 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **67 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **225 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **225 metro-4car trainsets / 900 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bhopal rail network on OpenStreetMap](bhopal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 67 / 15 |
| Route length | 168.1 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 225 × 4-car `metro-4car` trainsets (201 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.9 km | 10 | 40 | E Mid ↔ W Mid |
| line-2 | 18.1 km | 9 | 36 | S Mid ↔ N Mid |
| line-3 | 17.7 km | 9 | 36 | S Mid ↔ N Mid |
| line-4 | 30.9 km | 12 | 50 | SW Mid ↔ NE Outer |
| line-5 | 22.8 km | 9 | 38 | NW Mid ↔ SE Outer |
| line-6 | 57.7 km | 18 | 25 | NW Mid ↔ W Mid |
| **Total** | **168.1 km** | **67 unique** | **225** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 64,755 train-km/day |
| Annual traction demand | 408.4 GWh |
| Station/depot PV / storage | 47.1 MW / 325.5 MWh |
| Aggregate charging power | 94.5 MW |
| Dedicated solar plant | 160.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 16.2 km / 174 kWh |
| Lowest traversal charging margin | line-5: 171 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.59 bn |
| Stations | $386 M |
| Depots | $112 M |
| Rolling stock | $252 M |
| Dedicated solar plant | $128 M |
| Residual train control | $8.4 M |
| Charging microgrids | $19 M |
| EPC / project services | $165 M |
| **Total city programme** | **$2.66 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $526 M (19.8%) |
| Domestic / local capital | $2.13 bn (80.2%) |
| Annual public construction commitment | $232 M / yr for 5 years |
| Annual post-grace debt service | $165 M / yr |
| External capital saved vs default turnkey sensitivity | $4.26 bn |
| Capital + lifetime external interest saved | $9.49 bn |
| Annual OPEX | $63 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 601 assets / 3,229 tasks | [`bhopal-operations-manifest.json`](operations/bhopal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bhopal.toml`](bhopal.toml) | Expanded simulator scenario |
| [`bhopal.corridor.geojson`](bhopal.corridor.geojson) | GIS corridor and stations |
| [`bhopal.design-quality.yaml`](bhopal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bhopal
```
