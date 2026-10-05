# Uige — Urban Rail Network

**Country:** AO · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Uige-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$206 M (88.4%) of external capital** and **$253 M of external interest**. Capital plus saved interest totals **$458 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **12.025 km to 6.267 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **3 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**1 line-local depots** provide **24 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **24 light-metro-3car trainsets / 72 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Uige rail network on OpenStreetMap](uige-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 1 / 3 / 0 |
| Route length | 7.0 km double track |
| Coverage / transfer reachability | 13.1% / 100% |
| Estimated station catchment | 52,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 24 × 3-car `light-metro-3car` trainsets (21 peak revenue) |
| Peak network throughput | 14,400 passengers/hour |
| Practical service capacity | 133,920 passenger-trips/day |
| Annual paid-trip planning range | 24.4–39.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.0 km | 3 | 24 | NW Outer ↔ SE Outer |
| **Total** | **7.0 km** | **3 unique** | **24** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 465 one-way journeys / 3,262 train-km/day |
| Annual traction demand | 15.4 GWh |
| Station/depot PV / storage | 5.6 MW / 41.0 MWh |
| Aggregate charging power | 1.5 MW |
| Dedicated solar plant | 3.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 4.7 km / 35 kWh |
| Lowest traversal charging margin | line-1: 32 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $68 M |
| Stations | $12 M |
| Depots | $15 M |
| Rolling stock | $22 M |
| Dedicated solar plant | $3.0 M |
| Residual train control | $351 k |
| Charging microgrids | $450 k |
| EPC / project services | $8.3 M |
| **Total city programme** | **$129 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $27 M (20.9%) |
| Domestic / local capital | $102 M (79.1%) |
| Annual public construction commitment | $15 M / yr for 5 years |
| Annual post-grace debt service | $11 M / yr |
| External capital saved vs default turnkey sensitivity | $206 M |
| Capital + lifetime external interest saved | $458 M |
| Annual OPEX | $3.8 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 46 assets / 271 tasks | [`uige-operations-manifest.json`](operations/uige-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`uige.toml`](uige.toml) | Expanded simulator scenario |
| [`uige.corridor.geojson`](uige.corridor.geojson) | GIS corridor and stations |
| [`uige.design-quality.yaml`](uige.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh uige
```
