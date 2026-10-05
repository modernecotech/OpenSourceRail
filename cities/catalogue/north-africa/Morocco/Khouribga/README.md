# Khouribga — Urban Rail Network

**Country:** MA · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khouribga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$449 M (89.4%) of external capital** and **$552 M of external interest**. Capital plus saved interest totals **$1.00 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **18.788 km to 13.918 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **9 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **39 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **39 tram-2car trainsets / 78 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Khouribga rail network on OpenStreetMap](khouribga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 9 / 1 |
| Route length | 15.5 km double track |
| Coverage / transfer reachability | 58.6% / 33% |
| Estimated station catchment | 146,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 39 × 2-car `tram-2car` trainsets (33 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  6.8 km | 3 | 15 | S Outer ↔ E Outer |
| line-2 |  5.0 km | 3 | 13 | N Mid ↔ SW Outer |
| line-3 |  3.7 km | 3 | 11 | NW Mid ↔ S Inner |
| **Total** | **15.5 km** | **9 unique** | **39** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 7,228 train-km/day |
| Annual traction demand | 22.8 GWh |
| Station/depot PV / storage | 16.8 MW / 123.0 MWh |
| Aggregate charging power | 4.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.8 km / 21 kWh |
| Lowest traversal charging margin | line-2: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $152 M |
| Stations | $46 M |
| Depots | $39 M |
| Rolling stock | $22 M |
| Residual train control | $777 k |
| Charging microgrids | $1.1 M |
| EPC / project services | $18 M |
| **Total city programme** | **$279 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $53 M (19.0%) |
| Domestic / local capital | $226 M (81.0%) |
| Annual public construction commitment | $20 M / yr for 5 years |
| Annual post-grace debt service | $13 M / yr |
| External capital saved vs default turnkey sensitivity | $449 M |
| Capital + lifetime external interest saved | $1.00 bn |
| Annual OPEX | $8.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 97 assets / 510 tasks | [`khouribga-operations-manifest.json`](operations/khouribga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khouribga.toml`](khouribga.toml) | Expanded simulator scenario |
| [`khouribga.corridor.geojson`](khouribga.corridor.geojson) | GIS corridor and stations |
| [`khouribga.design-quality.yaml`](khouribga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh khouribga
```
