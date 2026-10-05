# Malanje — Urban Rail Network

**Country:** AO · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Malanje-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$399 M (88.6%) of external capital** and **$490 M of external interest**. Capital plus saved interest totals **$889 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **15.047 km to 11.929 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **7 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **44 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **44 light-metro-3car trainsets / 132 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Malanje rail network on OpenStreetMap](malanje-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 7 / 0 |
| Route length | 13.2 km double track |
| Coverage / transfer reachability | 59.2% / 0% |
| Estimated station catchment | 296,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 44 × 3-car `light-metro-3car` trainsets (39 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.1 km | 4 | 27 | W Outer ↔ E Outer |
| line-2 |  5.1 km | 3 | 17 | SE Mid ↔ NW Mid |
| **Total** | **13.2 km** | **7 unique** | **44** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 6,121 train-km/day |
| Annual traction demand | 29.0 GWh |
| Station/depot PV / storage | 11.5 MW / 82.5 MWh |
| Aggregate charging power | 3.5 MW |
| Dedicated solar plant | 5.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 3.7 km / 27 kWh |
| Lowest traversal charging margin | line-2: 27 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $133 M |
| Stations | $26 M |
| Depots | $29 M |
| Rolling stock | $40 M |
| Dedicated solar plant | $4.6 M |
| Residual train control | $658 k |
| Charging microgrids | $850 k |
| EPC / project services | $16 M |
| **Total city programme** | **$250 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $52 M (20.6%) |
| Domestic / local capital | $199 M (79.4%) |
| Annual public construction commitment | $29 M / yr for 5 years |
| Annual post-grace debt service | $22 M / yr |
| External capital saved vs default turnkey sensitivity | $399 M |
| Capital + lifetime external interest saved | $889 M |
| Annual OPEX | $7.1 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 91 assets / 523 tasks | [`malanje-operations-manifest.json`](operations/malanje-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`malanje.toml`](malanje.toml) | Expanded simulator scenario |
| [`malanje.corridor.geojson`](malanje.corridor.geojson) | GIS corridor and stations |
| [`malanje.design-quality.yaml`](malanje.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh malanje
```
