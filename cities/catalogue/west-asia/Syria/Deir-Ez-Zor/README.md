# Deir-Ez-Zor — Urban Rail Network

**Country:** SY · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Deir-Ez-Zor-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.34 bn (88.6%) of external capital** and **$1.73 bn of external interest**. Capital plus saved interest totals **$3.06 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **41.984 km to 36.434 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **18 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **155 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **155 light-metro-3car trainsets / 465 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Deir-Ez-Zor rail network on OpenStreetMap](deir-ez-zor-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 49.3 km double track |
| Coverage / transfer reachability | 58.0% / 33% |
| Estimated station catchment | 290,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 155 × 3-car `light-metro-3car` trainsets (140 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.6 km | 7 | 65 | NW Outer ↔ SE Outer |
| line-2 | 12.8 km | 5 | 39 | N Mid ↔ SW Mid |
| line-3 | 15.9 km | 6 | 51 | NE Outer ↔ SW Mid |
| **Total** | **49.3 km** | **18 unique** | **155** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 22,933 train-km/day |
| Annual traction demand | 108.5 GWh |
| Station/depot PV / storage | 18.6 MW / 126.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 35.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 10.0 km / 81 kWh |
| Lowest traversal charging margin | line-2: 29 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $487 M |
| Stations | $69 M |
| Depots | $58 M |
| Rolling stock | $140 M |
| Dedicated solar plant | $28 M |
| Residual train control | $2.5 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $53 M |
| **Total city programme** | **$838 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $173 M (20.6%) |
| Domestic / local capital | $666 M (79.4%) |
| Annual public construction commitment | $128 M / yr for 10 years |
| Annual post-grace debt service | $118 M / yr |
| External capital saved vs default turnkey sensitivity | $1.34 bn |
| Capital + lifetime external interest saved | $3.06 bn |
| Annual OPEX | $19 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 273 assets / 1,722 tasks | [`deir-ez-zor-operations-manifest.json`](operations/deir-ez-zor-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`deir-ez-zor.toml`](deir-ez-zor.toml) | Expanded simulator scenario |
| [`deir-ez-zor.corridor.geojson`](deir-ez-zor.corridor.geojson) | GIS corridor and stations |
| [`deir-ez-zor.design-quality.yaml`](deir-ez-zor.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh deir-ez-zor
```
