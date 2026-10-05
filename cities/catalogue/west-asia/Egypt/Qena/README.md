# Qena — Urban Rail Network

**Country:** EG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Qena-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.24 bn (88.9%) of external capital** and **$1.52 bn of external interest**. Capital plus saved interest totals **$2.76 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **41.769 km to 30.905 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **12 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **127 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **127 light-metro-3car trainsets / 381 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Qena rail network on OpenStreetMap](qena-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 12 / 0 |
| Route length | 41.4 km double track |
| Coverage / transfer reachability | 18.7% / 0% |
| Estimated station catchment | 65,450 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 127 × 3-car `light-metro-3car` trainsets (114 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.3 km | 4 | 31 | NE Mid ↔ SW Mid |
| line-2 | 17.9 km | 5 | 57 | W Mid ↔ SE Outer |
| line-3 | 13.2 km | 3 | 39 | W Inner ↔ N Outer |
| **Total** | **41.4 km** | **12 unique** | **127** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,250 train-km/day |
| Annual traction demand | 91.1 GWh |
| Station/depot PV / storage | 17.4 MW / 128.0 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 27.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.9 km / 88 kWh |
| Lowest traversal charging margin | line-1: 137 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $490 M |
| Stations | $41 M |
| Depots | $53 M |
| Rolling stock | $114 M |
| Dedicated solar plant | $22 M |
| Residual train control | $2.1 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $49 M |
| **Total city programme** | **$774 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $154 M (19.9%) |
| Domestic / local capital | $620 M (80.1%) |
| Annual public construction commitment | $84 M / yr for 5 years |
| Annual post-grace debt service | $63 M / yr |
| External capital saved vs default turnkey sensitivity | $1.24 bn |
| Capital + lifetime external interest saved | $2.76 bn |
| Annual OPEX | $20 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 5 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 213 assets / 1,366 tasks | [`qena-operations-manifest.json`](operations/qena-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`qena.toml`](qena.toml) | Expanded simulator scenario |
| [`qena.corridor.geojson`](qena.corridor.geojson) | GIS corridor and stations |
| [`qena.design-quality.yaml`](qena.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh qena
```
