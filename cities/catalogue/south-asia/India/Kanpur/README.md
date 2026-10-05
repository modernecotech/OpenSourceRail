# Kanpur — Urban Rail Network

**Country:** IN · **Population:** 3,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kanpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$46.75 bn (90.9%) of external capital** and **$57.47 bn of external interest**. Capital plus saved interest totals **$104.22 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **303.964 km to 322.833 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **144 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **533 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **533 metro-6car trainsets / 3198 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Kanpur rail network on OpenStreetMap](kanpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 144 / 25 |
| Route length | 359.5 km double track |
| Direct transfers / reachable line pairs | 82.1% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 533 × 6-car `metro-6car` trainsets (482 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.0 km | 11 | 50 | SE Mid ↔ NW Mid |
| line-2 | 25.4 km | 11 | 51 | NW Mid ↔ SE Inner |
| line-3 | 64.6 km | 31 | 131 | W Outer ↔ E Outer |
| line-4 | 38.5 km | 15 | 71 | SW Mid ↔ NE Outer |
| line-5 | 26.5 km | 11 | 51 | E Mid ↔ W Outer |
| line-6 | 45.9 km | 14 | 87 | N Outer ↔ S Outer |
| line-7 | 20.6 km | 9 | 40 | SW Outer ↔ SE Inner |
| line-8 | 113.0 km | 42 | 52 | NW Mid ↔ NW Mid |
| **Total** | **359.5 km** | **144 unique** | **533** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 140,885 train-km/day |
| Annual traction demand | 1,332.9 GWh |
| Station/depot PV / storage | 78.1 MW / 574.0 MWh |
| Aggregate charging power | 270.0 MW |
| Dedicated solar plant | 610.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 13.9 km / 224 kWh |
| Lowest traversal charging margin | line-7: 157 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $24.21 bn |
| Stations | $847 M |
| Depots | $231 M |
| Rolling stock | $895 M |
| Dedicated solar plant | $488 M |
| Residual train control | $18 M |
| Charging microgrids | $55 M |
| EPC / project services | $1.84 bn |
| **Total city programme** | **$28.58 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.70 bn (16.4%) |
| Domestic / local capital | $23.88 bn (83.6%) |
| Annual public construction commitment | $2.54 bn / yr for 5 years |
| Annual post-grace debt service | $1.78 bn / yr |
| External capital saved vs default turnkey sensitivity | $46.75 bn |
| Capital + lifetime external interest saved | $104.22 bn |
| Annual OPEX | $568 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 31 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,339 assets / 7,407 tasks | [`kanpur-operations-manifest.json`](operations/kanpur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kanpur.toml`](kanpur.toml) | Expanded simulator scenario |
| [`kanpur.corridor.geojson`](kanpur.corridor.geojson) | GIS corridor and stations |
| [`kanpur.design-quality.yaml`](kanpur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kanpur
```
