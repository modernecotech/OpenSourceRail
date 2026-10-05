# Jinja — Urban Rail Network

**Country:** UG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jinja-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.36 bn (90.9%) of external capital** and **$4.22 bn of external interest**. Capital plus saved interest totals **$7.58 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **32.128 km to 30.487 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **22 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **90 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **90 tram-2car trainsets / 180 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Jinja rail network on OpenStreetMap](jinja-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 1 |
| Route length | 43.2 km double track |
| Coverage / transfer reachability | 65.1% / 100% |
| Estimated station catchment | 195,300 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 90 × 2-car `tram-2car` trainsets (80 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.0 km | 7 | 28 | NE Outer ↔ S Inner |
| line-2 | 17.4 km | 8 | 35 | SE Mid ↔ NW Mid |
| line-3 | 12.8 km | 7 | 27 | SW Outer ↔ NE Mid |
| **Total** | **43.2 km** | **22 unique** | **90** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 20,067 train-km/day |
| Annual traction demand | 63.3 GWh |
| Station/depot PV / storage | 20.4 MW / 129.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 18.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.3 km / 37 kWh |
| Lowest traversal charging margin | line-3: 44 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.68 bn |
| Stations | $125 M |
| Depots | $45 M |
| Rolling stock | $50 M |
| Dedicated solar plant | $14 M |
| Residual train control | $2.2 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $133 M |
| **Total city programme** | **$2.05 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $335 M (16.3%) |
| Domestic / local capital | $1.72 bn (83.7%) |
| Annual public construction commitment | $257 M / yr for 7 years |
| Annual post-grace debt service | $215 M / yr |
| External capital saved vs default turnkey sensitivity | $3.36 bn |
| Capital + lifetime external interest saved | $7.58 bn |
| Annual OPEX | $41 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 220 assets / 1,207 tasks | [`jinja-operations-manifest.json`](operations/jinja-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jinja.toml`](jinja.toml) | Expanded simulator scenario |
| [`jinja.corridor.geojson`](jinja.corridor.geojson) | GIS corridor and stations |
| [`jinja.design-quality.yaml`](jinja.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jinja
```
