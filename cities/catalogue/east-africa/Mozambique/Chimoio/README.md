# Chimoio — Urban Rail Network

**Country:** MZ · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Chimoio-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$739 M (88.1%) of external capital** and **$954 M of external interest**. Capital plus saved interest totals **$1.69 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **28.174 km to 22.675 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **94 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **94 light-metro-3car trainsets / 282 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Chimoio rail network on OpenStreetMap](chimoio-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 11 / 1 |
| Route length | 29.7 km double track |
| Coverage / transfer reachability | 32.9% / 100% |
| Estimated station catchment | 131,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 94 × 3-car `light-metro-3car` trainsets (85 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.1 km | 6 | 54 | E Outer ↔ SW Outer |
| line-2 | 12.6 km | 5 | 40 | E Outer ↔ W Mid |
| **Total** | **29.7 km** | **11 unique** | **94** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 13,825 train-km/day |
| Annual traction demand | 65.4 GWh |
| Station/depot PV / storage | 12.1 MW / 83.5 MWh |
| Aggregate charging power | 4.5 MW |
| Dedicated solar plant | 29.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 53 kWh |
| Lowest traversal charging margin | line-2: 43 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $255 M |
| Stations | $34 M |
| Depots | $37 M |
| Rolling stock | $85 M |
| Dedicated solar plant | $23 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.1 M |
| EPC / project services | $29 M |
| **Total city programme** | **$466 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $100 M (21.5%) |
| Domestic / local capital | $366 M (78.5%) |
| Annual public construction commitment | $51 M / yr for 10 years |
| Annual post-grace debt service | $47 M / yr |
| External capital saved vs default turnkey sensitivity | $739 M |
| Capital + lifetime external interest saved | $1.69 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 167 assets / 1,045 tasks | [`chimoio-operations-manifest.json`](operations/chimoio-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`chimoio.toml`](chimoio.toml) | Expanded simulator scenario |
| [`chimoio.corridor.geojson`](chimoio.corridor.geojson) | GIS corridor and stations |
| [`chimoio.design-quality.yaml`](chimoio.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh chimoio
```
