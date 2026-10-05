# Faisalabad — Urban Rail Network

**Country:** PK · **Population:** 3,556,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Faisalabad-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.11 bn (88.1%) of external capital** and **$5.15 bn of external interest**. Capital plus saved interest totals **$9.26 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **146.999 km to 119.745 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **51 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **232 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **232 metro-6car trainsets / 1392 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Faisalabad rail network on OpenStreetMap](faisalabad-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 51 / 9 |
| Route length | 150.3 km double track |
| Coverage / transfer reachability | 65.6% / 73% |
| Estimated station catchment | 2,332,736 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 232 × 6-car `metro-6car` trainsets (208 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.9 km | 8 | 51 | SW Mid ↔ NE Outer |
| line-2 | 19.6 km | 7 | 36 | NE Mid ↔ W Mid |
| line-3 | 19.6 km | 8 | 38 | SE Mid ↔ W Mid |
| line-4 | 20.9 km | 7 | 41 | NW Mid ↔ S Mid |
| line-5 | 24.1 km | 7 | 46 | N Mid ↔ SW Outer |
| line-6 | 39.2 km | 14 | 20 | W Inner ↔ W Inner |
| **Total** | **150.3 km** | **51 unique** | **232** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 60,790 train-km/day |
| Annual traction demand | 575.1 GWh |
| Station/depot PV / storage | 42.6 MW / 324.0 MWh |
| Aggregate charging power | 96.0 MW |
| Dedicated solar plant | 229.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 12.2 km / 204 kWh |
| Lowest traversal charging margin | line-5: 145 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.45 bn |
| Stations | $253 M |
| Depots | $130 M |
| Rolling stock | $390 M |
| Dedicated solar plant | $184 M |
| Residual train control | $7.5 M |
| Charging microgrids | $20 M |
| EPC / project services | $157 M |
| **Total city programme** | **$2.59 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $555 M (21.4%) |
| Domestic / local capital | $2.04 bn (78.6%) |
| Annual public construction commitment | $352 M / yr for 7 years |
| Annual post-grace debt service | $303 M / yr |
| External capital saved vs default turnkey sensitivity | $4.11 bn |
| Capital + lifetime external interest saved | $9.26 bn |
| Annual OPEX | $61 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 530 assets / 3,009 tasks | [`faisalabad-operations-manifest.json`](operations/faisalabad-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`faisalabad.toml`](faisalabad.toml) | Expanded simulator scenario |
| [`faisalabad.corridor.geojson`](faisalabad.corridor.geojson) | GIS corridor and stations |
| [`faisalabad.design-quality.yaml`](faisalabad.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh faisalabad
```
