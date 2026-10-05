# Nairobi — Urban Rail Network

**Country:** KE · **Population:** 5,700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nairobi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.24 bn (87.3%) of external capital** and **$14.09 bn of external interest**. Capital plus saved interest totals **$25.32 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **393.543 km to 333.214 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **132 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **698 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **698 metro-6car trainsets / 4188 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nairobi rail network on OpenStreetMap](nairobi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 132 / 18 |
| Route length | 451.3 km double track |
| Coverage / transfer reachability | 55.4% / 50% |
| Estimated station catchment | 3,157,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 698 × 6-car `metro-6car` trainsets (629 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 51.6 km | 17 | 96 | NE Outer ↔ SW Mid |
| line-2 | 43.9 km | 14 | 83 | E Outer ↔ W Mid |
| line-3 | 44.2 km | 13 | 82 | NW Mid ↔ SE Outer |
| line-4 | 27.8 km | 9 | 53 | E Mid ↔ W Mid |
| line-5 | 42.6 km | 10 | 78 | NE Mid ↔ SW Outer |
| line-6 | 55.1 km | 16 | 102 | SE Outer ↔ NW Outer |
| line-7 | 46.7 km | 14 | 89 | NW Outer ↔ SE Mid |
| line-8 | 38.9 km | 10 | 69 | SW Mid ↔ N Mid |
| line-9 | 100.5 km | 29 | 46 | W Mid ↔ W Mid |
| **Total** | **451.3 km** | **132 unique** | **698** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 186,490 train-km/day |
| Annual traction demand | 1,764.3 GWh |
| Station/depot PV / storage | 73.8 MW / 552.0 MWh |
| Aggregate charging power | 210.0 MW |
| Dedicated solar plant | 1,073.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 17.3 km / 260 kWh |
| Lowest traversal charging margin | line-8: 241 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.85 bn |
| Stations | $509 M |
| Depots | $288 M |
| Rolling stock | $1.17 bn |
| Dedicated solar plant | $859 M |
| Residual train control | $23 M |
| Charging microgrids | $43 M |
| EPC / project services | $412 M |
| **Total city programme** | **$7.15 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.64 bn (22.9%) |
| Domestic / local capital | $5.52 bn (77.1%) |
| Annual public construction commitment | $739 M / yr for 7 years |
| Annual post-grace debt service | $618 M / yr |
| External capital saved vs default turnkey sensitivity | $11.24 bn |
| Capital + lifetime external interest saved | $25.32 bn |
| Annual OPEX | $174 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 52 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,453 assets / 8,626 tasks | [`nairobi-operations-manifest.json`](operations/nairobi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nairobi.toml`](nairobi.toml) | Expanded simulator scenario |
| [`nairobi.corridor.geojson`](nairobi.corridor.geojson) | GIS corridor and stations |
| [`nairobi.design-quality.yaml`](nairobi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nairobi
```
