# Thika — Urban Rail Network

**Country:** KE · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Thika-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.63 bn (87.9%) of external capital** and **$2.04 bn of external interest**. Capital plus saved interest totals **$3.67 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **53.545 km to 46.516 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **22 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **215 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **215 light-metro-3car trainsets / 645 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Thika rail network on OpenStreetMap](thika-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 2 |
| Route length | 68.2 km double track |
| Coverage / transfer reachability | 50.8% / 67% |
| Estimated station catchment | 177,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 215 × 3-car `light-metro-3car` trainsets (194 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.1 km | 9 | 83 | SW Outer ↔ NE Outer |
| line-2 | 18.3 km | 6 | 57 | E Mid ↔ W Outer |
| line-3 | 23.8 km | 7 | 75 | SW Outer ↔ NE Outer |
| **Total** | **68.2 km** | **22 unique** | **215** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 31,708 train-km/day |
| Annual traction demand | 150.0 GWh |
| Station/depot PV / storage | 19.2 MW / 134.0 MWh |
| Aggregate charging power | 17.0 MW |
| Dedicated solar plant | 76.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 13.5 km / 101 kWh |
| Lowest traversal charging margin | line-2: 290 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $558 M |
| Stations | $80 M |
| Depots | $66 M |
| Rolling stock | $194 M |
| Dedicated solar plant | $61 M |
| Residual train control | $3.4 M |
| Charging microgrids | $3.7 M |
| EPC / project services | $63 M |
| **Total city programme** | **$1.03 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $224 M (21.8%) |
| Domestic / local capital | $805 M (78.2%) |
| Annual public construction commitment | $107 M / yr for 7 years |
| Annual post-grace debt service | $89 M / yr |
| External capital saved vs default turnkey sensitivity | $1.63 bn |
| Capital + lifetime external interest saved | $3.67 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 360 assets / 2,335 tasks | [`thika-operations-manifest.json`](operations/thika-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`thika.toml`](thika.toml) | Expanded simulator scenario |
| [`thika.corridor.geojson`](thika.corridor.geojson) | GIS corridor and stations |
| [`thika.design-quality.yaml`](thika.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh thika
```
