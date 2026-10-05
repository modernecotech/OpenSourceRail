# Sumbawanga — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sumbawanga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$328 M (89.1%) of external capital** and **$411 M of external interest**. Capital plus saved interest totals **$740 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **15.698 km to 9.228 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **8 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **31 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **31 tram-2car trainsets / 62 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sumbawanga rail network on OpenStreetMap](sumbawanga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 8 / 1 |
| Route length | 9.9 km double track |
| Coverage / transfer reachability | 59.0% / 33% |
| Estimated station catchment | 147,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 31 × 2-car `tram-2car` trainsets (25 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  3.8 km | 3 | 11 | E Mid ↔ NW Outer |
| line-2 |  4.1 km | 3 | 12 | S Outer ↔ NE Mid |
| line-3 |  2.0 km | 2 | 8 | NW Mid ↔ SW Mid |
| **Total** | **9.9 km** | **8 unique** | **31** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 4,585 train-km/day |
| Annual traction demand | 14.5 GWh |
| Station/depot PV / storage | 16.5 MW / 122.5 MWh |
| Aggregate charging power | 4.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 2.1 km / 12 kWh |
| Lowest traversal charging margin | line-3: 37 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $96 M |
| Stations | $38 M |
| Depots | $38 M |
| Rolling stock | $17 M |
| Residual train control | $493 k |
| Charging microgrids | $950 k |
| EPC / project services | $13 M |
| **Total city programme** | **$205 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $40 M (19.7%) |
| Domestic / local capital | $164 M (80.3%) |
| Annual public construction commitment | $19 M / yr for 7 years |
| Annual post-grace debt service | $16 M / yr |
| External capital saved vs default turnkey sensitivity | $328 M |
| Capital + lifetime external interest saved | $740 M |
| Annual OPEX | $5.4 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 83 assets / 419 tasks | [`sumbawanga-operations-manifest.json`](operations/sumbawanga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sumbawanga.toml`](sumbawanga.toml) | Expanded simulator scenario |
| [`sumbawanga.corridor.geojson`](sumbawanga.corridor.geojson) | GIS corridor and stations |
| [`sumbawanga.design-quality.yaml`](sumbawanga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sumbawanga
```
