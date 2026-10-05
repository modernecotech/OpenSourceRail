# Kandahar — Urban Rail Network

**Country:** AF · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kandahar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.09 bn (88.5%) of external capital** and **$1.40 bn of external interest**. Capital plus saved interest totals **$2.49 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **48.775 km to 35.001 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **16 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **129 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **129 light-metro-3car trainsets / 387 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kandahar rail network on OpenStreetMap](kandahar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 0 |
| Route length | 42.6 km double track |
| Coverage / transfer reachability | 16.1% / 0% |
| Estimated station catchment | 112,700 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 129 × 3-car `light-metro-3car` trainsets (116 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.7 km | 6 | 52 | NE Mid ↔ W Outer |
| line-2 | 14.1 km | 5 | 43 | SE Outer ↔ N Mid |
| line-3 | 10.9 km | 5 | 34 | SW Mid ↔ E Mid |
| **Total** | **42.6 km** | **16 unique** | **129** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,826 train-km/day |
| Annual traction demand | 93.8 GWh |
| Station/depot PV / storage | 18.9 MW / 126.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 27.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 4.8 km / 39 kWh |
| Lowest traversal charging margin | line-3: 26 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $390 M |
| Stations | $52 M |
| Depots | $54 M |
| Rolling stock | $116 M |
| Dedicated solar plant | $22 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $43 M |
| **Total city programme** | **$681 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $141 M (20.7%) |
| Domestic / local capital | $540 M (79.3%) |
| Annual public construction commitment | $95 M / yr for 10 years |
| Annual post-grace debt service | $87 M / yr |
| External capital saved vs default turnkey sensitivity | $1.09 bn |
| Capital + lifetime external interest saved | $2.49 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 236 assets / 1,460 tasks | [`kandahar-operations-manifest.json`](operations/kandahar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kandahar.toml`](kandahar.toml) | Expanded simulator scenario |
| [`kandahar.corridor.geojson`](kandahar.corridor.geojson) | GIS corridor and stations |
| [`kandahar.design-quality.yaml`](kandahar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kandahar
```
