# Damietta — Urban Rail Network

**Country:** EG · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damietta-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.47 bn (88.1%) of external capital** and **$1.81 bn of external interest**. Capital plus saved interest totals **$3.28 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **47.639 km to 37.944 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **21 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **200 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **200 light-metro-3car trainsets / 600 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Damietta rail network on OpenStreetMap](damietta-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 0 |
| Route length | 65.4 km double track |
| Coverage / transfer reachability | 47.4% / 0% |
| Estimated station catchment | 189,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 200 × 3-car `light-metro-3car` trainsets (180 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.3 km | 8 | 69 | N Outer ↔ S Outer |
| line-2 | 17.3 km | 5 | 53 | SE Mid ↔ NW Outer |
| line-3 | 25.8 km | 8 | 78 | SW Outer ↔ NE Outer |
| **Total** | **65.4 km** | **21 unique** | **200** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 30,432 train-km/day |
| Annual traction demand | 144.0 GWh |
| Station/depot PV / storage | 20.1 MW / 128.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 52.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-2: 51 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $512 M |
| Stations | $67 M |
| Depots | $64 M |
| Rolling stock | $180 M |
| Dedicated solar plant | $42 M |
| Residual train control | $3.3 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $58 M |
| **Total city programme** | **$929 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $199 M (21.5%) |
| Domestic / local capital | $729 M (78.5%) |
| Annual public construction commitment | $99 M / yr for 5 years |
| Annual post-grace debt service | $75 M / yr |
| External capital saved vs default turnkey sensitivity | $1.47 bn |
| Capital + lifetime external interest saved | $3.28 bn |
| Annual OPEX | $26 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 341 assets / 2,195 tasks | [`damietta-operations-manifest.json`](operations/damietta-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damietta.toml`](damietta.toml) | Expanded simulator scenario |
| [`damietta.corridor.geojson`](damietta.corridor.geojson) | GIS corridor and stations |
| [`damietta.design-quality.yaml`](damietta.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh damietta
```
