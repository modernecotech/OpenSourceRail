# Kabul — Urban Rail Network

**Country:** AF · **Population:** 4,601,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kabul-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.19 bn (88.0%) of external capital** and **$6.71 bn of external interest**. Capital plus saved interest totals **$11.90 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **194.539 km to 154.789 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **69 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **296 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **296 metro-6car trainsets / 1776 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kabul rail network on OpenStreetMap](kabul-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 69 / 14 |
| Route length | 193.8 km double track |
| Coverage / transfer reachability | 45.6% / 48% |
| Estimated station catchment | 2,098,056 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 296 × 6-car `metro-6car` trainsets (265 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.4 km | 9 | 45 | NE Outer ↔ W Mid |
| line-2 | 26.5 km | 9 | 50 | SE Mid ↔ NW Outer |
| line-3 | 18.4 km | 9 | 40 | W Mid ↔ NE Mid |
| line-4 | 25.9 km | 9 | 50 | SW Outer ↔ E Outer |
| line-5 | 28.6 km | 10 | 51 | NW Mid ↔ E Outer |
| line-6 | 18.1 km | 7 | 35 | SE Outer ↔ N Inner |
| line-7 | 52.8 km | 16 | 25 | W Mid ↔ NW Mid |
| **Total** | **193.8 km** | **69 unique** | **296** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,022 one-way journeys / 77,815 train-km/day |
| Annual traction demand | 736.2 GWh |
| Station/depot PV / storage | 52.7 MW / 398.0 MWh |
| Aggregate charging power | 132.0 MW |
| Dedicated solar plant | 313.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 8.3 km / 120 kWh |
| Lowest traversal charging margin | line-6: 237 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.79 bn |
| Stations | $349 M |
| Depots | $158 M |
| Rolling stock | $497 M |
| Dedicated solar plant | $251 M |
| Residual train control | $9.7 M |
| Charging microgrids | $27 M |
| EPC / project services | $198 M |
| **Total city programme** | **$3.28 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $710 M (21.7%) |
| Domestic / local capital | $2.57 bn (78.3%) |
| Annual public construction commitment | $453 M / yr for 10 years |
| Annual post-grace debt service | $416 M / yr |
| External capital saved vs default turnkey sensitivity | $5.19 bn |
| Capital + lifetime external interest saved | $11.90 bn |
| Annual OPEX | $73 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 24 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 696 assets / 3,916 tasks | [`kabul-operations-manifest.json`](operations/kabul-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kabul.toml`](kabul.toml) | Expanded simulator scenario |
| [`kabul.corridor.geojson`](kabul.corridor.geojson) | GIS corridor and stations |
| [`kabul.design-quality.yaml`](kabul.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kabul
```
