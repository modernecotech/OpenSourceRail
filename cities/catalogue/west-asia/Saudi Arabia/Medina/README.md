# Medina — Urban Rail Network

**Country:** SA · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Medina-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.06 bn (89.0%) of external capital** and **$4.99 bn of external interest**. Capital plus saved interest totals **$9.06 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **148.772 km to 130.020 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **59 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **211 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **211 metro-4car trainsets / 844 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Medina rail network on OpenStreetMap](medina-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 59 / 10 |
| Route length | 168.6 km double track |
| Coverage / transfer reachability | 44.3% / 47% |
| Estimated station catchment | 664,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 211 × 4-car `metro-4car` trainsets (189 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.9 km | 12 | 52 | NW Outer ↔ SE Outer |
| line-2 | 19.1 km | 8 | 35 | SW Mid ↔ NE Mid |
| line-3 | 18.3 km | 7 | 31 | NW Mid ↔ S Mid |
| line-4 | 23.3 km | 9 | 40 | NE Mid ↔ W Outer |
| line-5 | 18.3 km | 5 | 29 | N Mid ↔ E Outer |
| line-6 | 57.6 km | 18 | 24 | E Outer ↔ E Mid |
| **Total** | **168.6 km** | **59 unique** | **211** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 65,018 train-km/day |
| Annual traction demand | 410.1 GWh |
| Station/depot PV / storage | 44.7 MW / 313.5 MWh |
| Aggregate charging power | 82.5 MW |
| Dedicated solar plant | 163.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 12.7 km / 136 kWh |
| Lowest traversal charging margin | line-5: 114 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.58 bn |
| Stations | $291 M |
| Depots | $111 M |
| Rolling stock | $236 M |
| Dedicated solar plant | $131 M |
| Residual train control | $8.4 M |
| Charging microgrids | $17 M |
| EPC / project services | $157 M |
| **Total city programme** | **$2.53 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $500 M (19.7%) |
| Domestic / local capital | $2.03 bn (80.3%) |
| Annual public construction commitment | $177 M / yr for 5 years |
| Annual post-grace debt service | $122 M / yr |
| External capital saved vs default turnkey sensitivity | $4.06 bn |
| Capital + lifetime external interest saved | $9.06 bn |
| Annual OPEX | $112 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 545 assets / 2,957 tasks | [`medina-operations-manifest.json`](operations/medina-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`medina.toml`](medina.toml) | Expanded simulator scenario |
| [`medina.corridor.geojson`](medina.corridor.geojson) | GIS corridor and stations |
| [`medina.design-quality.yaml`](medina.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh medina
```
