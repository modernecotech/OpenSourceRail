# Phnom-Penh — Urban Rail Network

**Country:** KH · **Population:** 2,281,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Phnom-Penh-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$15.65 bn (90.4%) of external capital** and **$19.62 bn of external interest**. Capital plus saved interest totals **$35.27 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **180.759 km to 184.931 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **118 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **374 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **374 metro-4car trainsets / 1496 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Phnom-Penh rail network on OpenStreetMap](phnom-penh-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 118 / 15 |
| Route length | 244.7 km double track |
| Coverage / transfer reachability | 58.7% / 100% |
| Estimated station catchment | 1,338,947 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 374 × 4-car `metro-4car` trainsets (336 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.3 km | 11 | 47 | S Outer ↔ NW Mid |
| line-2 | 26.3 km | 11 | 46 | W Mid ↔ SE Outer |
| line-3 | 55.0 km | 33 | 115 | SW Outer ↔ NE Outer |
| line-4 | 36.9 km | 24 | 82 | N Mid ↔ S Outer |
| line-5 | 34.7 km | 15 | 58 | NW Outer ↔ SE Mid |
| line-6 | 64.5 km | 24 | 26 | NW Inner ↔ W Mid |
| **Total** | **244.7 km** | **118 unique** | **374** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 98,796 train-km/day |
| Annual traction demand | 623.1 GWh |
| Station/depot PV / storage | 59.1 MW / 385.5 MWh |
| Aggregate charging power | 154.5 MW |
| Dedicated solar plant | 341.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 18.7 km / 187 kWh |
| Lowest traversal charging margin | line-5: 207 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $7.43 bn |
| Stations | $704 M |
| Depots | $142 M |
| Rolling stock | $419 M |
| Dedicated solar plant | $273 M |
| Residual train control | $12 M |
| Charging microgrids | $31 M |
| EPC / project services | $612 M |
| **Total city programme** | **$9.62 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.67 bn (17.4%) |
| Domestic / local capital | $7.95 bn (82.6%) |
| Annual public construction commitment | $811 M / yr for 7 years |
| Annual post-grace debt service | $651 M / yr |
| External capital saved vs default turnkey sensitivity | $15.65 bn |
| Capital + lifetime external interest saved | $35.27 bn |
| Annual OPEX | $200 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 16 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,017 assets / 5,467 tasks | [`phnom-penh-operations-manifest.json`](operations/phnom-penh-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`phnom-penh.toml`](phnom-penh.toml) | Expanded simulator scenario |
| [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson) | GIS corridor and stations |
| [`phnom-penh.design-quality.yaml`](phnom-penh.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh phnom-penh
```
