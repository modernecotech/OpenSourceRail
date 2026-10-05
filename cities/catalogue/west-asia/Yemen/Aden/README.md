# Aden — Urban Rail Network

**Country:** YE · **Population:** 985,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aden-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.04 bn (88.4%) of external capital** and **$1.35 bn of external interest**. Capital plus saved interest totals **$2.39 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **41.033 km to 31.888 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **15 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **125 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **125 light-metro-3car trainsets / 375 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Aden rail network on OpenStreetMap](aden-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 1 |
| Route length | 40.2 km double track |
| Coverage / transfer reachability | 52.5% / 33% |
| Estimated station catchment | 517,125 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 125 × 3-car `light-metro-3car` trainsets (112 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.0 km | 6 | 46 | NW Outer ↔ S Mid |
| line-2 | 11.5 km | 4 | 36 | NE Mid ↔ SW Outer |
| line-3 | 13.8 km | 5 | 43 | N Outer ↔ SE Outer |
| **Total** | **40.2 km** | **15 unique** | **125** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,704 train-km/day |
| Annual traction demand | 88.5 GWh |
| Station/depot PV / storage | 18.6 MW / 126.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 25.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.9 km / 56 kWh |
| Lowest traversal charging margin | line-2: 29 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $362 M |
| Stations | $63 M |
| Depots | $53 M |
| Rolling stock | $112 M |
| Dedicated solar plant | $20 M |
| Residual train control | $2.0 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $42 M |
| **Total city programme** | **$655 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $136 M (20.8%) |
| Domestic / local capital | $519 M (79.2%) |
| Annual public construction commitment | $91 M / yr for 10 years |
| Annual post-grace debt service | $84 M / yr |
| External capital saved vs default turnkey sensitivity | $1.04 bn |
| Capital + lifetime external interest saved | $2.39 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 226 assets / 1,405 tasks | [`aden-operations-manifest.json`](operations/aden-operations-manifest.json) |

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
