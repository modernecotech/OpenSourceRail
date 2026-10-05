# Cuenca — Urban Rail Network

**Country:** EC · **Population:** 817,100 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Cuenca-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.41 bn (87.9%) of external capital** and **$1.73 bn of external interest**. Capital plus saved interest totals **$3.14 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **53.360 km to 38.728 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **21 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **185 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **185 light-metro-3car trainsets / 555 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Cuenca rail network on OpenStreetMap](cuenca-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 58.5 km double track |
| Coverage / transfer reachability | 45.3% / 33% |
| Estimated station catchment | 370,146 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 185 × 3-car `light-metro-3car` trainsets (167 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.3 km | 7 | 64 | E Mid ↔ W Outer |
| line-2 | 19.0 km | 7 | 61 | NE Outer ↔ W Mid |
| line-3 | 19.1 km | 7 | 60 | NW Mid ↔ SE Outer |
| **Total** | **58.5 km** | **21 unique** | **185** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 27,190 train-km/day |
| Annual traction demand | 128.6 GWh |
| Station/depot PV / storage | 19.2 MW / 127.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 62.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.6 km / 87 kWh |
| Lowest traversal charging margin | line-3: 63 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $480 M |
| Stations | $70 M |
| Depots | $62 M |
| Rolling stock | $166 M |
| Dedicated solar plant | $50 M |
| Residual train control | $2.9 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $55 M |
| **Total city programme** | **$889 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $193 M (21.7%) |
| Domestic / local capital | $696 M (78.3%) |
| Annual public construction commitment | $89 M / yr for 5 years |
| Annual post-grace debt service | $66 M / yr |
| External capital saved vs default turnkey sensitivity | $1.41 bn |
| Capital + lifetime external interest saved | $3.14 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 321 assets / 2,046 tasks | [`cuenca-operations-manifest.json`](operations/cuenca-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`cuenca.toml`](cuenca.toml) | Expanded simulator scenario |
| [`cuenca.corridor.geojson`](cuenca.corridor.geojson) | GIS corridor and stations |
| [`cuenca.design-quality.yaml`](cuenca.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh cuenca
```
