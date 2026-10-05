# Kitale — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kitale-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$802 M (89.4%) of external capital** and **$1.00 bn of external interest**. Capital plus saved interest totals **$1.81 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **32.967 km to 26.793 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **74 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **74 tram-2car trainsets / 148 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kitale rail network on OpenStreetMap](kitale-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 1 |
| Route length | 36.5 km double track |
| Coverage / transfer reachability | 49.1% / 33% |
| Estimated station catchment | 147,300 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 74 × 2-car `tram-2car` trainsets (66 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.6 km | 4 | 26 | W Mid ↔ SE Outer |
| line-2 | 13.4 km | 4 | 27 | SW Outer ↔ NE Mid |
| line-3 | 10.4 km | 3 | 21 | SE Inner ↔ N Outer |
| **Total** | **36.5 km** | **11 unique** | **74** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 16,949 train-km/day |
| Annual traction demand | 53.5 GWh |
| Station/depot PV / storage | 17.1 MW / 127.0 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 15.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 9.6 km / 48 kWh |
| Lowest traversal charging margin | line-3: 114 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $316 M |
| Stations | $49 M |
| Depots | $43 M |
| Rolling stock | $41 M |
| Dedicated solar plant | $12 M |
| Residual train control | $1.8 M |
| Charging microgrids | $2.3 M |
| EPC / project services | $32 M |
| **Total city programme** | **$498 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $95 M (19.0%) |
| Domestic / local capital | $403 M (81.0%) |
| Annual public construction commitment | $53 M / yr for 7 years |
| Annual post-grace debt service | $44 M / yr |
| External capital saved vs default turnkey sensitivity | $802 M |
| Capital + lifetime external interest saved | $1.81 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 147 assets / 863 tasks | [`kitale-operations-manifest.json`](operations/kitale-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kitale.toml`](kitale.toml) | Expanded simulator scenario |
| [`kitale.corridor.geojson`](kitale.corridor.geojson) | GIS corridor and stations |
| [`kitale.design-quality.yaml`](kitale.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kitale
```
