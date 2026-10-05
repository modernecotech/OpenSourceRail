# Agra — Urban Rail Network

**Country:** IN · **Population:** 1,700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Agra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.67 bn (89.2%) of external capital** and **$4.52 bn of external interest**. Capital plus saved interest totals **$8.19 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **147.193 km to 126.375 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **51 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **176 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **176 metro-4car trainsets / 704 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Agra rail network on OpenStreetMap](agra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 51 / 10 |
| Route length | 144.7 km double track |
| Coverage / transfer reachability | 39.6% / 70% |
| Estimated station catchment | 673,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 176 × 4-car `metro-4car` trainsets (156 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.6 km | 9 | 38 | NW Mid ↔ SE Outer |
| line-2 | 21.5 km | 8 | 35 | S Mid ↔ NE Outer |
| line-3 | 20.0 km | 8 | 35 | NE Outer ↔ W Mid |
| line-4 | 28.0 km | 10 | 45 | SE Outer ↔ NW Outer |
| line-5 | 54.6 km | 16 | 23 | W Mid ↔ W Mid |
| **Total** | **144.7 km** | **51 unique** | **176** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 54,593 train-km/day |
| Annual traction demand | 344.3 GWh |
| Station/depot PV / storage | 37.9 MW / 264.5 MWh |
| Aggregate charging power | 72.0 MW |
| Dedicated solar plant | 137.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 7.8 km / 84 kWh |
| Lowest traversal charging margin | line-2: 137 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.48 bn |
| Stations | $247 M |
| Depots | $92 M |
| Rolling stock | $197 M |
| Dedicated solar plant | $110 M |
| Residual train control | $7.2 M |
| Charging microgrids | $15 M |
| EPC / project services | $142 M |
| **Total city programme** | **$2.29 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $443 M (19.4%) |
| Domestic / local capital | $1.84 bn (80.6%) |
| Annual public construction commitment | $200 M / yr for 5 years |
| Annual post-grace debt service | $142 M / yr |
| External capital saved vs default turnkey sensitivity | $3.67 bn |
| Capital + lifetime external interest saved | $8.19 bn |
| Annual OPEX | $53 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 464 assets / 2,500 tasks | [`agra-operations-manifest.json`](operations/agra-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`agra.toml`](agra.toml) | Expanded simulator scenario |
| [`agra.corridor.geojson`](agra.corridor.geojson) | GIS corridor and stations |
| [`agra.design-quality.yaml`](agra.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh agra
```
