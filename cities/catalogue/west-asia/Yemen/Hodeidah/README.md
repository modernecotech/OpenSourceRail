# Hodeidah — Urban Rail Network

**Country:** YE · **Population:** 750,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hodeidah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$684 M (88.6%) of external capital** and **$884 M of external interest**. Capital plus saved interest totals **$1.57 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **30.741 km to 21.335 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **12 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **78 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **78 light-metro-3car trainsets / 234 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hodeidah rail network on OpenStreetMap](hodeidah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 12 / 0 |
| Route length | 23.4 km double track |
| Coverage / transfer reachability | 49.0% / 0% |
| Estimated station catchment | 367,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 78 × 3-car `light-metro-3car` trainsets (70 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.5 km | 4 | 26 | NE Mid ↔ S Outer |
| line-2 |  9.8 km | 5 | 32 | SE Mid ↔ NW Outer |
| line-3 |  6.1 km | 3 | 20 | E Outer ↔ NW Mid |
| **Total** | **23.4 km** | **12 unique** | **78** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 10,901 train-km/day |
| Annual traction demand | 51.6 GWh |
| Station/depot PV / storage | 17.7 MW / 124.5 MWh |
| Aggregate charging power | 6.0 MW |
| Dedicated solar plant | 6.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.1 km / 25 kWh |
| Lowest traversal charging margin | line-3: 19 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $229 M |
| Stations | $48 M |
| Depots | $46 M |
| Rolling stock | $70 M |
| Dedicated solar plant | $5.4 M |
| Residual train control | $1.2 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $28 M |
| **Total city programme** | **$429 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $88 M (20.5%) |
| Domestic / local capital | $341 M (79.5%) |
| Annual public construction commitment | $60 M / yr for 10 years |
| Annual post-grace debt service | $55 M / yr |
| External capital saved vs default turnkey sensitivity | $684 M |
| Capital + lifetime external interest saved | $1.57 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 157 assets / 921 tasks | [`hodeidah-operations-manifest.json`](operations/hodeidah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hodeidah.toml`](hodeidah.toml) | Expanded simulator scenario |
| [`hodeidah.corridor.geojson`](hodeidah.corridor.geojson) | GIS corridor and stations |
| [`hodeidah.design-quality.yaml`](hodeidah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hodeidah
```
