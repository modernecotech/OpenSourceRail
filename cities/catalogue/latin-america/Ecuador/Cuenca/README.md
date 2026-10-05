# Cuenca — Urban Rail Network

**Country:** EC · **Population:** 817,100 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Cuenca-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.44 bn (87.9%) of external capital** and **$1.77 bn of external interest**. Capital plus saved interest totals **$3.21 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **53.360 km to 43.517 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **22 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **188 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **188 light-metro-3car trainsets / 564 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Cuenca rail network on OpenStreetMap](cuenca-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 2 |
| Route length | 59.8 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 135,707 (2020 raster; 24.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 188 × 3-car `light-metro-3car` trainsets (170 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.1 km | 7 | 65 | E Mid ↔ W Outer |
| line-2 | 19.6 km | 7 | 62 | NE Outer ↔ W Mid |
| line-3 | 19.2 km | 8 | 61 | NW Mid ↔ SE Outer |
| **Total** | **59.8 km** | **22 unique** | **188** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 27,822 train-km/day |
| Annual traction demand | 131.6 GWh |
| Station/depot PV / storage | 19.5 MW / 127.5 MWh |
| Aggregate charging power | 9.0 MW |
| Dedicated solar plant | 64.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 12.1 km / 91 kWh |
| Lowest traversal charging margin | line-2: 63 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $484 M |
| Stations | $82 M |
| Depots | $62 M |
| Rolling stock | $169 M |
| Dedicated solar plant | $51 M |
| Residual train control | $3.0 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $56 M |
| **Total city programme** | **$910 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $198 M (21.7%) |
| Domestic / local capital | $712 M (78.3%) |
| Annual public construction commitment | $92 M / yr for 5 years |
| Annual post-grace debt service | $68 M / yr |
| External capital saved vs default turnkey sensitivity | $1.44 bn |
| Capital + lifetime external interest saved | $3.21 bn |
| Annual OPEX | $28 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 330 assets / 2,092 tasks | [`cuenca-operations-manifest.json`](operations/cuenca-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`cuenca.toml`](cuenca.toml) | Expanded simulator scenario |
| [`cuenca.corridor.geojson`](cuenca.corridor.geojson) | GIS corridor and stations |
| [`cuenca.design-quality.yaml`](cuenca.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh cuenca
```
