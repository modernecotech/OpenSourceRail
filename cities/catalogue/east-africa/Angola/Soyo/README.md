# Soyo — Urban Rail Network

**Country:** AO · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Soyo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$613 M (89.4%) of external capital** and **$754 M of external interest**. Capital plus saved interest totals **$1.37 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **25.547 km to 15.369 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **19 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **46 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **46 tram-2car trainsets / 92 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Soyo rail network on OpenStreetMap](soyo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 2 |
| Route length | 21.0 km double track |
| Coverage / transfer reachability | 15.1% / 100% |
| Estimated station catchment | 37,750 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 46 × 2-car `tram-2car` trainsets (40 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  6.9 km | 6 | 15 | NW Outer ↔ SE Inner |
| line-2 |  3.9 km | 4 | 10 | S Inner ↔ E Mid |
| line-3 | 10.2 km | 9 | 21 | N Mid ↔ SE Outer |
| **Total** | **21.0 km** | **19 unique** | **46** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 9,756 train-km/day |
| Annual traction demand | 30.8 GWh |
| Station/depot PV / storage | 19.8 MW / 136.0 MWh |
| Aggregate charging power | 19.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 1.4 km / 7 kWh |
| Lowest traversal charging margin | line-2: 142 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $187 M |
| Stations | $98 M |
| Depots | $40 M |
| Rolling stock | $26 M |
| Residual train control | $1.0 M |
| Charging microgrids | $4.3 M |
| EPC / project services | $25 M |
| **Total city programme** | **$381 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $73 M (19.1%) |
| Domestic / local capital | $308 M (80.9%) |
| Annual public construction commitment | $44 M / yr for 5 years |
| Annual post-grace debt service | $33 M / yr |
| External capital saved vs default turnkey sensitivity | $613 M |
| Capital + lifetime external interest saved | $1.37 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 155 assets / 754 tasks | [`soyo-operations-manifest.json`](operations/soyo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`soyo.toml`](soyo.toml) | Expanded simulator scenario |
| [`soyo.corridor.geojson`](soyo.corridor.geojson) | GIS corridor and stations |
| [`soyo.design-quality.yaml`](soyo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh soyo
```
