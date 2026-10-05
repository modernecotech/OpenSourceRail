# Aden — Urban Rail Network

**Country:** YE · **Population:** 985,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aden-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.78 bn (91.1%) of external capital** and **$10.05 bn of external interest**. Capital plus saved interest totals **$17.82 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **41.033 km to 42.878 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **23 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **156 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **156 light-metro-3car trainsets / 468 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Aden rail network on OpenStreetMap](aden-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 4 |
| Route length | 47.7 km double track |
| Coverage / transfer reachability | 58.6% / 100% |
| Estimated station catchment | 577,210 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 156 × 3-car `light-metro-3car` trainsets (140 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.2 km | 9 | 65 | NW Outer ↔ S Outer |
| line-2 | 13.7 km | 7 | 45 | NE Mid ↔ SW Outer |
| line-3 | 13.8 km | 7 | 46 | N Outer ↔ SE Outer |
| **Total** | **47.7 km** | **23 unique** | **156** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 22,174 train-km/day |
| Annual traction demand | 104.9 GWh |
| Station/depot PV / storage | 21.0 MW / 130.0 MWh |
| Aggregate charging power | 11.5 MW |
| Dedicated solar plant | 30.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.7 km / 38 kWh |
| Lowest traversal charging margin | line-3: 49 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.07 bn |
| Stations | $138 M |
| Depots | $58 M |
| Rolling stock | $140 M |
| Dedicated solar plant | $25 M |
| Residual train control | $2.4 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $309 M |
| **Total city programme** | **$4.74 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $761 M (16.0%) |
| Domestic / local capital | $3.98 bn (84.0%) |
| Annual public construction commitment | $687 M / yr for 10 years |
| Annual post-grace debt service | $624 M / yr |
| External capital saved vs default turnkey sensitivity | $7.78 bn |
| Capital + lifetime external interest saved | $17.82 bn |
| Annual OPEX | $93 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 302 assets / 1,833 tasks | [`aden-operations-manifest.json`](operations/aden-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aden.toml`](aden.toml) | Expanded simulator scenario |
| [`aden.corridor.geojson`](aden.corridor.geojson) | GIS corridor and stations |
| [`aden.design-quality.yaml`](aden.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh aden
```
