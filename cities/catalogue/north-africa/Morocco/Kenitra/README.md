# Kenitra — Urban Rail Network

**Country:** MA · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kenitra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.33 bn (88.3%) of external capital** and **$1.64 bn of external interest**. Capital plus saved interest totals **$2.97 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **48.553 km to 40.788 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **21 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **163 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **163 light-metro-3car trainsets / 489 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kenitra rail network on OpenStreetMap](kenitra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 2 |
| Route length | 51.8 km double track |
| Coverage / transfer reachability | 59.8% / 67% |
| Estimated station catchment | 299,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 163 × 3-car `light-metro-3car` trainsets (147 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.1 km | 8 | 51 | E Mid ↔ W Mid |
| line-2 | 16.7 km | 6 | 51 | SE Mid ↔ W Outer |
| line-3 | 19.9 km | 7 | 61 | SW Mid ↔ NE Outer |
| **Total** | **51.8 km** | **21 unique** | **163** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,072 train-km/day |
| Annual traction demand | 113.9 GWh |
| Station/depot PV / storage | 20.1 MW / 128.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 42.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 9.3 km / 67 kWh |
| Lowest traversal charging margin | line-3: 63 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $451 M |
| Stations | $89 M |
| Depots | $60 M |
| Rolling stock | $147 M |
| Dedicated solar plant | $34 M |
| Residual train control | $2.6 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $53 M |
| **Total city programme** | **$838 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $177 M (21.1%) |
| Domestic / local capital | $661 M (78.9%) |
| Annual public construction commitment | $58 M / yr for 5 years |
| Annual post-grace debt service | $40 M / yr |
| External capital saved vs default turnkey sensitivity | $1.33 bn |
| Capital + lifetime external interest saved | $2.97 bn |
| Annual OPEX | $25 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 299 assets / 1,857 tasks | [`kenitra-operations-manifest.json`](operations/kenitra-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kenitra.toml`](kenitra.toml) | Expanded simulator scenario |
| [`kenitra.corridor.geojson`](kenitra.corridor.geojson) | GIS corridor and stations |
| [`kenitra.design-quality.yaml`](kenitra.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kenitra
```
