# Damietta — Urban Rail Network

**Country:** EG · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damietta-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.64 bn (88.2%) of external capital** and **$2.02 bn of external interest**. Capital plus saved interest totals **$3.66 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **47.639 km to 41.632 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **24 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **208 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **208 light-metro-3car trainsets / 624 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Damietta rail network on OpenStreetMap](damietta-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 24 / 3 |
| Route length | 68.1 km double track |
| Coverage / transfer reachability | 47.6% / 100% |
| Estimated station catchment | 190,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 208 × 3-car `light-metro-3car` trainsets (188 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.1 km | 9 | 69 | N Outer ↔ S Outer |
| line-2 | 17.8 km | 7 | 54 | SE Mid ↔ W Outer |
| line-3 | 27.3 km | 8 | 85 | SW Outer ↔ NE Outer |
| **Total** | **68.1 km** | **24 unique** | **208** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 31,668 train-km/day |
| Annual traction demand | 149.8 GWh |
| Station/depot PV / storage | 20.4 MW / 129.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 55.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 13.5 km / 109 kWh |
| Lowest traversal charging margin | line-2: 39 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $557 M |
| Stations | $110 M |
| Depots | $65 M |
| Rolling stock | $187 M |
| Dedicated solar plant | $44 M |
| Residual train control | $3.4 M |
| Charging microgrids | $2.3 M |
| EPC / project services | $65 M |
| **Total city programme** | **$1.03 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $220 M (21.2%) |
| Domestic / local capital | $815 M (78.8%) |
| Annual public construction commitment | $111 M / yr for 5 years |
| Annual post-grace debt service | $83 M / yr |
| External capital saved vs default turnkey sensitivity | $1.64 bn |
| Capital + lifetime external interest saved | $3.66 bn |
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
| Operations, QA and maintenance | 364 assets / 2,315 tasks | [`damietta-operations-manifest.json`](operations/damietta-operations-manifest.json) |

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
