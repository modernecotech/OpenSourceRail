# Vijayawada — Urban Rail Network

**Country:** IN · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Vijayawada-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.51 bn (88.7%) of external capital** and **$5.54 bn of external interest**. Capital plus saved interest totals **$10.05 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **178.684 km to 142.223 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **57 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **240 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **240 metro-4car trainsets / 960 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Vijayawada rail network on OpenStreetMap](vijayawada-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 57 / 10 |
| Route length | 194.4 km double track |
| Coverage / transfer reachability | 72.6% / 53% |
| Estimated station catchment | 1,089,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 240 × 4-car `metro-4car` trainsets (214 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.9 km | 12 | 47 | NW Outer ↔ SE Mid |
| line-2 | 23.3 km | 8 | 38 | NE Mid ↔ SW Outer |
| line-3 | 33.8 km | 10 | 56 | E Outer ↔ W Outer |
| line-4 | 22.7 km | 7 | 38 | E Mid ↔ NW Outer |
| line-5 | 20.4 km | 6 | 34 | E Inner ↔ S Outer |
| line-6 | 67.2 km | 14 | 27 | NW Mid ↔ W Inner |
| **Total** | **194.4 km** | **57 unique** | **240** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 74,784 train-km/day |
| Annual traction demand | 471.7 GWh |
| Station/depot PV / storage | 42.6 MW / 303.0 MWh |
| Aggregate charging power | 72.0 MW |
| Dedicated solar plant | 260.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 12.1 km / 121 kWh |
| Lowest traversal charging margin | line-4: 118 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.77 bn |
| Stations | $260 M |
| Depots | $116 M |
| Rolling stock | $269 M |
| Dedicated solar plant | $208 M |
| Residual train control | $9.7 M |
| Charging microgrids | $15 M |
| EPC / project services | $171 M |
| **Total city programme** | **$2.82 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $571 M (20.3%) |
| Domestic / local capital | $2.25 bn (79.7%) |
| Annual public construction commitment | $245 M / yr for 5 years |
| Annual post-grace debt service | $175 M / yr |
| External capital saved vs default turnkey sensitivity | $4.51 bn |
| Capital + lifetime external interest saved | $10.05 bn |
| Annual OPEX | $66 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 563 assets / 3,166 tasks | [`vijayawada-operations-manifest.json`](operations/vijayawada-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`vijayawada.toml`](vijayawada.toml) | Expanded simulator scenario |
| [`vijayawada.corridor.geojson`](vijayawada.corridor.geojson) | GIS corridor and stations |
| [`vijayawada.design-quality.yaml`](vijayawada.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh vijayawada
```
