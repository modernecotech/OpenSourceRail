# Entebbe — Urban Rail Network

**Country:** UG · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Entebbe-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$470 M (87.7%) of external capital** and **$589 M of external interest**. Capital plus saved interest totals **$1.06 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Entebbe rail network on OpenStreetMap](entebbe-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 38.9 km double track |
| Coverage / transfer reachability | 76.3% / 100% |
| Estimated station catchment | 190,750 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 78 × 2-car `tram-2car` trainsets (70 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.5 km | 7 | 30 | NE Outer ↔ W Mid |
| line-2 |  7.9 km | 4 | 17 | SW Mid ↔ W Mid |
| line-3 | 15.5 km | 6 | 31 | S Mid ↔ NE Outer |
| **Total** | **38.9 km** | **17 unique** | **78** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,098 train-km/day |
| Annual traction demand | 57.1 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 26.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.5 km / 33 kWh |
| Lowest traversal charging margin | line-2: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $113 M |
| Stations | $90 M |
| Depots | $8.0 M |
| Rolling stock | $44 M |
| Dedicated solar plant | $21 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $18 M |
| **Total city programme** | **$298 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $66 M (22.2%) |
| Domestic / local capital | $231 M (77.8%) |
| Annual public construction commitment | $36 M / yr for 7 years |
| Annual post-grace debt service | $30 M / yr |
| External capital saved vs default turnkey sensitivity | $470 M |
| Capital + lifetime external interest saved | $1.06 bn |
| Annual OPEX | $7.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 179 assets / 806 tasks | [`entebbe-operations-manifest.json`](operations/entebbe-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`entebbe.toml`](entebbe.toml) | Expanded simulator scenario |
| [`entebbe.corridor.geojson`](entebbe.corridor.geojson) | GIS corridor and stations |
| [`entebbe.design-quality.yaml`](entebbe.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh entebbe
```
