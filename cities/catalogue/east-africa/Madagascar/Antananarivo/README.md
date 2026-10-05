# Antananarivo — Urban Rail Network

**Country:** MG · **Population:** 3,058,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Antananarivo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.22 bn (87.8%) of external capital** and **$10.61 bn of external interest**. Capital plus saved interest totals **$18.83 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **266.865 km to 224.295 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **88 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **449 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **449 metro-6car trainsets / 2694 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Antananarivo rail network on OpenStreetMap](antananarivo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 88 / 17 |
| Route length | 291.2 km double track |
| Coverage / transfer reachability | 70.2% / 44% |
| Estimated station catchment | 2,146,716 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 449 × 6-car `metro-6car` trainsets (404 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.4 km | 8 | 50 | S Mid ↔ NE Outer |
| line-2 | 24.4 km | 8 | 47 | SE Mid ↔ NW Outer |
| line-3 | 28.8 km | 11 | 57 | W Outer ↔ E Mid |
| line-4 | 22.6 km | 7 | 42 | E Mid ↔ SW Mid |
| line-5 | 25.8 km | 10 | 51 | N Inner ↔ S Outer |
| line-6 | 32.1 km | 9 | 60 | E Outer ↔ W Outer |
| line-7 | 28.9 km | 9 | 54 | W Mid ↔ NE Outer |
| line-8 | 29.0 km | 8 | 54 | SE Mid ↔ NW Outer |
| line-9 | 71.2 km | 18 | 34 | NW Mid ↔ NW Mid |
| **Total** | **291.2 km** | **88 unique** | **449** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 118,868 train-km/day |
| Annual traction demand | 1,124.6 GWh |
| Station/depot PV / storage | 64.5 MW / 490.0 MWh |
| Aggregate charging power | 148.0 MW |
| Dedicated solar plant | 664.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 14.7 km / 220 kWh |
| Lowest traversal charging margin | line-8: 208 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.93 bn |
| Stations | $415 M |
| Depots | $221 M |
| Rolling stock | $754 M |
| Dedicated solar plant | $531 M |
| Residual train control | $15 M |
| Charging microgrids | $30 M |
| EPC / project services | $306 M |
| **Total city programme** | **$5.20 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.15 bn (22.0%) |
| Domestic / local capital | $4.06 bn (78.0%) |
| Annual public construction commitment | $490 M / yr for 10 years |
| Annual post-grace debt service | $444 M / yr |
| External capital saved vs default turnkey sensitivity | $8.22 bn |
| Capital + lifetime external interest saved | $18.83 bn |
| Annual OPEX | $116 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 960 assets / 5,608 tasks | [`antananarivo-operations-manifest.json`](operations/antananarivo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`antananarivo.toml`](antananarivo.toml) | Expanded simulator scenario |
| [`antananarivo.corridor.geojson`](antananarivo.corridor.geojson) | GIS corridor and stations |
| [`antananarivo.design-quality.yaml`](antananarivo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh antananarivo
```
